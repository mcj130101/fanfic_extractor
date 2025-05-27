
import subprocess
import os

url = "https://www.literotica.com/series/se/494221236"
url2 = "https://www.literotica.com/s/photography-assignment-pt-02"

filepath  = os.path.join("E:",  "Lit")
subprocess.run(
            ["fanficfare","-o", "is_adult=true", "-u", url2,  "-o", f"output_filename={filepath}"] ,
            capture_output=True,
            text=True,
            check=False,
        )