# Tiny FunC interpreter

## How to use:

```
./refunpy <input> [--ast-on] [--env-on]
```

## Example:

FunC programm:

```C
() draw(int rows, int lines, int multp) {
    (int min, int max) = (rows, lines * multp);

    while (min != 0) {
        while (max != 0) {
            if ((min == rows) | (min == 0) | (max == (lines * multp)) | (max == 0)) {
                ~strdump("#");
            } else {
                ~strdump(" ");
            }
            
            max -= 1;
        }  
        ~strdump("\n"); 
        min -= 1;
        max = lines * multp;
    }
}

() main() {
    (int rows, int lines) = (5, 5);
    draw(rows, lines, 10);
}
```

Output:

```shell
zpnst@debian ~/D/p/p/c/p/refunpy (master)> ./refunpy contrs/draw.func
###################################################
#                                                 #
#                                                 #
#                                                 #
#                                                 #
###################################################
```