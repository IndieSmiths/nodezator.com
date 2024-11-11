# Script and content for generating static website for https://nodezator.com

Just execute the generate.py script like this in this folder:

```
python3 generate.py
```

Depending on your system, you might have to replace `python3` by `python`.

It will read contents from the `content` folder and create a new sibling `output` folder with the generated website. If the `output` folder already exists at the time of the call, it is removed completely and then generated.

It relies solely on Python and its standard library.
