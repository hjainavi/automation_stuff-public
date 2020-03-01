BEGIN{print "mmap = {"}
{
    split(tolower($2),a,"(");
    split($2,b,"(");
    split($1,c,".py");
    sub(/..\//,"",c[1]);
    sub(/\//,".", c[1]);
    if (match(c[1], "^permission.*") == 0)   {
        sub(/(^A*)/, "api.", c[1]);
    }
    printf("\"%s\": (\"%s\", \"%s\"),\n", a[1], b[1], c[1]);
}
END {print "}"}
