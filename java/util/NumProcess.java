package codevault.java.util;

class NumProcess {

  /**
   * Checks is digit's order increasing
   */
  public static boolean isDigitsAsc(long num) {
    return Long.toString(num).chars()
      .map(d -> d - '0')
      .reduce(0, (a, b) -> {
        if (a <= b || a == 0) 
          return (a != -1) ? b : a;
        else 
          return -1;
      }) != -1;
  }
  
  public static long reverse(long num) {
    return Long.valueOf(new StringBuilder()
      .append(String.valueOf(num))
      .reverse()
      .toString()
    );
  }


  public static String digitsToString(int[] a) {
    return Arrays.stream(a)
      .boxed()
      .map(String::valueOf)
      .collect(Collectors.joining());
  }


  public static long digitsToLong(int[] a) {
    return Long.valueOf(digitsToString(a));
  }


  public static int digitsToInt(int[] a) {
    return Integer.valueOf(digitsToString(a));
  }

}