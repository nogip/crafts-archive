package dev.nogipx.java.run;

public class Kata {

  public static long nextBiggerNumber(long n) {
    if (isDigitsDesc(n)) return -1;
    String ns = String.valueOf(n);
    int nsl = ns.length();
    return Long.valueOf(ns.substring(0, nsl-2) + ns.charAt(nsl) + ns.charAt(nsl-1));
  }

  public static boolean isDigitsDesc(long num) {
    return String.valueOf(num).chars()
      .map(d -> d - '0')
      .reduce(0, (a, b) -> {
        if (a >= b || a == 0) 
          return (a != -1) ? b : a;
        else 
          return -1;
      }) != -1;
  }
}