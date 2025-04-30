# Tiny FunC interpreter

## How to use:

```
./refunpy <path> [--ast-on] [--env-on]
```

## Example:

FunC programm:

```C
{-
    Simple, 
        FunC programm!
-}

const A = 222;

int plus(int x, int y) impure inline {
    return x + y;
}

;; Hello!
(int, int) mult_plus(int x, int y) impure {
    return (
        plus(x * y, x * y) + A, 
        (plus(x * y, x * y) + 2) / 3
    );
}

;; This is STRDUMP TVM instruction!
() ~strLog(slice value) impure asm "STRDUMP";

() main() impure { ;; Main function!
    int hello = "Hello!\n"; ;; Hello!
    ~strLog(hello);

    (int res4, int res5) = mult_plus(1, 2);

    return (); {-
        Hello, World!
    -}
}
```

Output:

```shell
zpnst@debian ~/D/p/p/c/p/refunpy (v2)> ./refunpy contracts/p.func --env-on
Hello!
-- RES:  (('glob', (('A', 222),), 'funcs', ((('hello', '"Hello!\\n"'), ('res4', 226), ('res5', 2)),)),)
```