    /**
     * Generates efficient range.
     * @param count: digits in range
     */
    private static Map<Integer, Integer> generateRanges(int count) {
      Map<Integer, Integer> ranges = new HashMap();
      IntStream.range(11, 100)
        .forEach(x -> {
          int[] d = String.valueOf(x).chars().map(c -> c - '0').toArray();
          if (d[1] >= d[0]) 
            ranges.putAll(getRange(Integer.toString(x), count));
        });
        
      return ranges;
    }
  
    
    /**
     * @use getRange("18", 5) => 18888:18999
     * @use getRange("3", 5) => 33333:39999
     * @use getRange("666", 5) => 66666:66699
     */
    private static Map<Integer, Integer> getRange(String firstDigits, int count) {
      Map<Integer, Integer> ranges = new HashMap();
      int level = firstDigits.length();
      int repeatToFill = (count - level > 0) ? count - level : 0;
      
      String edgeDigit = String.valueOf(firstDigits.charAt(level - 1));
      String beginRange = firstDigits + edgeDigit.repeat(repeatToFill);
      String endRange = firstDigits + "9".repeat(repeatToFill);
      
      ranges.put(Integer.valueOf(beginRange), Integer.valueOf(endRange));
      
      return ranges;
    }

    private static int arrToInt(int[] a) {
      return Integer.valueOf(
        Arrays.stream(a)
          .boxed()
          .map(String::valueOf)
          .collect(Collectors.joining())
      );
    }