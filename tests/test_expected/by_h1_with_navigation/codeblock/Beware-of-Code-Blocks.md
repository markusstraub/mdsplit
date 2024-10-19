# Beware of Code Blocks

Hash(es) at the beginning of a line within a code block
do not represent headings:

```
# not a heading but a comment within a code block
## fake heading 2
```

```bash
# comment
touch /tmp/file.txt 
```

~~~
# also within a code block and not a heading 
~~~

#not a heading since the space after the hash is missing
##same goes for this line


---

[🡅](./toc.md)