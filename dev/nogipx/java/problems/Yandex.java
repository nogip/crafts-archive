package dev.nogipx.java.problems;

import java.util.*;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

class Yandex {

  public static void main(String[] args) {
    System.out.println(getRanges(List.of(1,2,3,4,6,7)));
    System.out.println(getRanges(List.of(0,1,2,5,6,8,10)));
    System.out.println(getRanges(List.of(4,7,10)));
    System.out.println(getRanges(List.of(1,2,3,3,6,7,10,11)));
    System.out.println(getRanges(List.of(7,1,2,3,6,7,10,11)));
  }
  
  public static String getRanges(List<Integer> l) {
    // Begin ranges & End ranges (br & er)
    List<Integer> br = new ArrayList<>();
    List<Integer> er = new ArrayList<>();

    l.stream().reduce(l.get(0)-2, (a, b) -> {
      if (Math.abs(a-b) > 1 && a < b) {
        er.add(a);
        br.add(b);
      }
      return b;
    });
    er.remove(0);
    er.add(l.get(l.size()-1));

    // Zip & join
    return IntStream
      .range(0, Math.min(br.size(), er.size()))
      .mapToObj(i -> (br.get(i) != er.get(i)) 
                      ? br.get(i) + "-" + er.get(i) 
                      : br.get(i) + "")
      .collect(Collectors.joining(", "));
  }
}
