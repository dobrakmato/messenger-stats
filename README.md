messenger-stats
---------------

![](https://i.imgur.com/HS6ko9c.png)

## Installation
Run `pip3 install -r requirements.txt`

## Usage
Download archive of all you data from Facebook using their awesome
 [export tool](https://www.facebook.com/help/302796099745838).

Unzip contents of the archive to folder of your choice.

### Run interactively
Run script interactively and paste path to console when asked for it:

```
./main.py
```

```
You invoked script as interactive shell.
--------------------------------------------------------------
Please enter path to unzipped Facebook export directory (the one which contains subfolders: html, messages).
Export root: (enter path here)
```


### Run with argument
Or run the script with the folder provided as first argument to script.

```
./main.py /path/to/unzipped/archive
```

```
You invoked script as interactive shell.
--------------------------------------------------------------
Using provided argument as path:  /path/to/unzipped/archive
--------------------------------------------------------------
```

### Use programmatically

You can also use script programmatically by creating instance
of `FacebookStatistics` class and then calling its methods.

```python
stats = FacebookStatistics('/path/to/unzipped/archive')
stats.parse_all_messages()

stats.global_stats()  # print global stats
```