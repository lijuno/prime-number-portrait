# Notes

- Original inspiration: Lex Friedman podcast https://www.youtube.com/watch?v=ndMahzDCH1Y

- Original implementation https://github.com/rmeertens/prime_portraits and its blog post http://www.pinchofintelligence.com/painting-by-prime-number/

- Something to improve:
  - It cannot render the face well if a little far away. The facial area had small area but also very important in a picture. Can introduce some simple facial recognition to add constraints on the search problem.
  - Color choice is not stable. The K-means colorization is random and not based on the chromatic distance. Need to make the colorization more sensible.
  - Make number of trials in the Miller-Rabin primality test bigger, such as 100 like in [ref](http://archive.bridgesmathart.org/2016/bridges2016-359.pdf)

- Some other interesting resources
  - Curation of prime numbers https://www.reddit.com/r/math/comments/c89d02/i_am_looking_for_a_big_database_of_primes/
  - Almost the ultimate resource on prime numbers https://primes.utm.edu/
  - Details of Miller–Rabin primality test https://en.wikipedia.org/wiki/Miller%E2%80%93Rabin_primality_test A good read

- Interestingly, the Python had built-in support for big integers so the modulo operation of big primes are handled without fuss by `pow()`. In C++, one will need library support such as [GMP](https://gmplib.org/), and [some Github repos](https://github.com/search?l=C%2B%2B&q=big+integer&type=Repositories). Rust had [big int library](https://github.com/rust-num/num-bigint) too. [This paper](https://secure-media.collegeboard.org/apc/ap01.pdf.lr_7928.pdf) had internal explanation of big ints in C++.
