import os, subprocess, feedparser, time, re
from pydub import AudioSegment

TIMEOUT = 300
PIPER_MODEL = " en_GB-aru-medium.onnx"
RSS_FEED_URL = "https://pluralistic.net/feed/"
REGEX_HYPERLINK = r'https?://(www.)?[-a-zA-Z0-9@:%.+~#=]{1,256}.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()!@:%+.~#?&//=]*)'

def fetch_feed(url):
    # result = feedparser.parse(url)
    result = feedparser.parse("./iTzxLVnH.rss")
    return result

# Function to process feed entries
def process_entries(entries):
    if not os.path.exists("out"):
        os.makedirs("out")
    for entry in entries:
        name_txt = "out/" + entry.author + " - " + "".join(c for c in entry.title if c.isalnum() or c in [' ', '.', '-']).rstrip() + ".txt"
        name_wav = name_txt[:-4] + ".wav"
        name_mp3 = name_txt[:-4] + ".mp3"
        if os.path.exists(name_mp3):# or os.path.exists(name_txt):
            print(f"File '{name_txt}' already processed, continuing")
            continue

        summary = entry.summary
        summary = re.sub(r'.*?\(permalink\)', '', summary, count=1, flags=re.DOTALL)
        summary = re.sub(REGEX_HYPERLINK, '', summary)
        summary = re.sub(r'&#8211; ', '- ', summary)
        summary = re.sub(r'This day in history.*', '', summary, flags=re.DOTALL)
        with open(name_txt, "w") as file:
            file.write(summary)

        subprocess.run(["echo", name_txt, "|", "piper", "--model", PIPER_MODEL, "--output_file", name_wav])
        input_wav = AudioSegment.from_file(name_wav)
        input_wav.export(name_mp3, format="mp3", bitrate="128k")
        os.remove(name_wav)

# Main function
def main():
    while True:
        try:
            feed = fetch_feed(RSS_FEED_URL)
            entries = feed.entries
            process_entries(entries)
        except Exception as e:
            print("An error occurred:", e)

        # Fetch the feed every 5 minutes
        time.sleep(TIMEOUT)

if __name__ == "__main__":
    main()
