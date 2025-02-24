from hrn_sdk.loader.hrn_loader import HRNLoader

def add_raw_sd_map_topic(hrn):
  loader = HRNLoader(hrn)

  loader = HRNLoader(hrn, groups=["sd_map"],)

if __name__ == "__main__":
  add_raw_sd_map_topic("aac")


iterator = loader.get_topic(topics=["/functions/hmi/sd_map"])