# TODO's
check why logfileinspector always has less frames then when we parse it in python or rust
build a scanner class and a reader class similar to python
add cool progressbars: https://github.com/clitic/kdam

It makes more sense to only implement the parts that need parsing of logs in rust and maybe we call rust functions from python


# Maybe
Should we replace everything with rust? That would mean we need to also replace the sdk in rust
- we still want to have the python sdk for use of analysis scripts so we would need to implement that twice if we do that in rust as well.