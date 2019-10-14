import java.util.*;
import java.util.stream.Collectors;

public class Scramblies {

  public static void main(String[] args) {
    System.out.println(scramble("qwfpgj","jgpfwq"));
    System.out.println(scramble("rkqodlw","world"));
    System.out.println(scramble("cedewaraaossoqqyt","codewars"));
    System.out.println(scramble("katas","steak"));
    System.out.println(scramble("scriptjavx","javascript"));
  }
    
  public static boolean scramble(String str1, String str2) {
    Map<String, Long> m1 = decomposeStr(str1);
    return decomposeStr(str2).entrySet().stream()
      .allMatch(e -> 
        m1.containsKey(e.getKey()) 
        && m1.get(e.getKey()) >= e.getValue()
      );
  }

  private static Map<String, Long> decomposeStr(String str) {
    return List.of(str.split("")).stream().parallel()
      .collect(Collectors.groupingBy(c -> c, Collectors.counting()));
  }
}