package codevault.java.util;

class DigitStream {

  public static IntStream of(int num) {
    return of(String.valueOf(num));
  }

  public static IntStream of(long num) {
    return of(String.valueOf(num));
  }

  public static IntStream of(String num) {
    return num.chars().map(d -> d - '0');
  }
}