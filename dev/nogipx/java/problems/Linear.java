package dev.nogipx.java.problems;

import java.util.*;
import java.util.stream.*;

class DoubleLinear {

  public static void main(String[] args) {
    System.out.println(dblLinear(50));
  }
 
  public static int dblLinear (int n) {
    Set<Integer> nums = new HashSet<>(50);    
    ArrayDeque<Node> queue = new ArrayDeque<>();

    Node root = new Node(1);
    queue.add(root);
    nums.add(root.v);

    while (nums.size() < n+1) {

      queue.stream()
        .forEach(x -> {
          x.y = new Node(2 * x.v + 1);
          x.z = new Node(3 * x.v + 1);
        });

      IntStream.range(0, queue.size())
        .forEach(i -> {
          Node x = queue.pollFirst();
          System.out.println(x.v);

          nums.add(x.y.v);
          nums.add(x.z.v);
          
          // Let complete layer calculation.
          if (nums.size() < n) {
            queue.add(x.y);
            queue.add(x.z);
          }
        });
    }

    List<Integer> numsList = new ArrayList<>(nums);
    Collections.sort(numsList);
    System.out.println(numsList);
    return numsList.get(n);
  }
}

class Node {
  Node y = null;
  Node z = null;
  int v = 0;

  public Node(int v) {
    this.v = v;
  }
}