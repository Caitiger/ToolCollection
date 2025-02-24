from saturnv_data_sdk.hrn.loader.hrn_loader import HRNLoader
from saturnv_data_sdk.hrn.index_operator.supplement_operator import build_supplement_index

from mcap.writer import Writer as McapWriter

import argparse
import os
import glob
import csv

ADD_TOPIC = "/functions/hmi/raw/sd_map"
SRC_TOPIC = "/functions/hmi/sd_map"

VERSION = "raw-sdmap-v0.0.1"

NEW_HRN_FILE_NAME = "hrn_new_final.txt"

def add_raw_sdmap_topic(hrn, output_path):
    loader = HRNLoader(hrn)

    project_id = loader.project_id
    device_id = loader.device_id

    topic_name_list = loader.get_topic_names(msg_type="mcap")


    if SRC_TOPIC in topic_name_list and ADD_TOPIC not in topic_name_list:
        print(f"now add {ADD_TOPIC} for {hrn}")

        iterator = loader.get_topic(topics=[SRC_TOPIC], decode=True)

        output_path = output_path + '/' + hrn.replace('/', '_').replace(':', '_') + '.mcap'
        print(output_path)

        writer = McapWriter(output_path)
        writer.start()

        is_registed = False

        for schema, channel ,message ,*extra in iterator:
            if not is_registed:
                schema_id = writer.register_schema(schema.name, schema.encoding, schema.data)

                channel_id = writer.register_channel(
                    ADD_TOPIC,
                    channel.message_encoding,
                    schema_id,
                    channel.metadata,
                )

                is_registed = True

            writer.add_message(
                channel_id,
                message.log_time,
                message.data,
                message.publish_time,
            )

        writer.finish()

        mcap_path = output_path.replace("/horizon-bucket", "dmpv2:/")
        print(mcap_path)

        hrn = build_supplement_index(
            project_id,
            device_id,
            mcap_path,
            "drivepath",
            VERSION)

        with open(NEW_HRN_FILE_NAME, "a") as f:
            f.write(str(hrn) + "\n")

        print(hrn)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path", type=str, required=True)
    parser.add_argument("--output_path", type=str, required=True)
    return parser.parse_args()

def main():
    # add_raw_sdmap_topic("hrn:GA20230001:clip:DZ211/20240814_103729_591-20240814_103746_103", "/horizon-bucket/saturn_v_dev/01_users/v-qun.zhang/test")

    args = parse_args()

    global NEW_HRN_FILE_NAME

    NEW_HRN_FILE_NAME = args.output_path + "/" + NEW_HRN_FILE_NAME
    if os.path.exists(NEW_HRN_FILE_NAME):
        os.remove(NEW_HRN_FILE_NAME)

    csv_files = glob.glob(os.path.join(args.input_path, "*.csv"))
    csv_files.sort()
    for csv_file in csv_files:
      print(csv_file)
      with open(csv_file, 'r') as file:
          reader = csv.reader(file)
          for row in reader:
              uuid, project_id, hrn = row
              print(f"now check {hrn}")
              add_raw_sdmap_topic(hrn, args.output_path)


if __name__ == "__main__":
    main()



