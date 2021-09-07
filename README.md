# Notes

- Original inspiration: Lex Friedman podcast https://www.youtube.com/watch?v=ndMahzDCH1Y

- Original implementation https://github.com/rmeertens/prime_portraits and its blog post http://www.pinchofintelligence.com/painting-by-prime-number/

- Something to improve:
  - It cannot render the face well if a little far away. The facial area had small area but also very important in a picture. Can introduce some simple facial recognition to add constraints on the search problem.
  - Color choice is not stable. The K-means colorization is random and not based on the chromatic distance. Need to make the colorization more sensible.
  - Make number of trials in the Miller-Rabin primality test bigger, such as 100 like in [ref](http://archive.bridgesmathart.org/2016/bridges2016-359.pdf)
