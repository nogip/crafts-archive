package codevault.java.util;
import codevault.java.util.DigitStream;
import codevault.java.util.NumProcess;

class Combinatorics {

  /**
   * Generates combinatory objects.
   */
  public static List<Long> genPartitions(int sum, int count) {
    List<Long> fragments = new ArrayList<>();
    // Logger log = Logger.getLogger(GenFragments.class.getName());
    
    // Step 1
    int[] a = DigitStream.of("1".repeat(count)).toArray();
    a[0] = sum-count+1;
    fragments.add(NumProcess.digitsToLong(a));

    while(true) {

      // Step 2 -> Step 3 -> Step 2
      while (!(a[1] >= a[0] - 1)) {
        a[0] -= 1;
        a[1] += 1;
        // log.info("[3] > " + NumProcess.digitsToLong(a));
        fragments.add(NumProcess.digitsToLong(a));
      }

      // Step 4
      int j = 2;
      int s = a[0] + a[1] - 1;
      while (j != a.length && !(a[j] < a[0] - 1)) {
        s += a[j];
        j += 1;
        // log.info("[4] > s="+s+" j="+j);
      }

      // Step 5
      int x = a[j-1]+1;
      if (j != a.length && !(j > count)) {
        x = a[j] + 1;
        a[j] = x;
        j -= 1;
        // log.info("[5] > " + NumProcess.digitsToLong(a));
        fragments.add(NumProcess.digitsToLong(a));
      } 
      else return fragments.stream()
        .filter(y -> DigitStream.of(y).sum() == sum)
        .collect(Collectors.toList());

      // Step 6
      while (j > 0) {
        a[j] = x;
        s -= x;
        j -= 1;
        a[0] = s;
        // log.info("[6] > " + NumProcess.digitsToLong(a));
        fragments.add(NumProcess.digitsToLong(a));
      }
    }
  }

}
