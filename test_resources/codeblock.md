# Header 1

some test

## Header 1.1

- a list
- with another entry
- and for good measure a third one

text before header
# Header 2 (dense)
and text after header
## Header 2.1
## Header 2.2

# Header 3 (with codeblocks)

this is the only case where a hash at the beginning of a line must be ignored:
```
# not a header but a comment within a code block
```

```bash
# comment
touch /tmp/file.txt 
```

~~~
# also within a codeblock and not a header 
~~~

# Header 4

#not a header since the space is lacking