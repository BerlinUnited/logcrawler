# Logcrawler
Docs can be found at https://docs.berlin-united.com/logcrawler/

## Development
You will need these environment variables in order to run the scripts:
```bash
VAT_LOG_ROOT=<"path to folder containing all the log data">
VAT_API_URL=<"http://127.0.0.1:8000/ or https://vat.berlin-united.com/">
VAT_API_TOKEN=<you need to ask the maintainer for a token>
```

For development we recommend using an .envrc file which enables you to quickly change those values.

### Access the log folder
If you have a large disk you can download the log folders in the correct structure to your disk and use the logs locally. This is recommended if you want to add a whole event to the database.

TODO: write scripts that downloads all necessary files
Alternatively you can use sshfs. This is much slower then using local files.
TODO add sshfs tutorial here


### The C part
The extract_images.py script needs to verify how many images are in the extracted folder. ls is really slow if you have a couple thousand files in one folder. We wrote our own fast_ls program that is much faster. The difference is most noteable if you access the log folder over network.

You can build the fast_ls binary with
```bash
gcc scripts/fast_ls.c -o fast_ls
```

### Build Rust Part
Install rust: https://doc.rust-lang.org/stable/book/ch01-01-installation.html

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt

maturin develop
python tests/rusty.py
```

You need to change the path to the logfile in the python script

TODO: explain the protos folder

### Ideas
Check where the ball rolls weird on the field