# P5 — Binary Search Tree
_hard · java · 23 submissions_

## Description

Implement a Binary Search Tree for `Integer` keys with the following API: `void insert(int key)` (idempotent on duplicates), `boolean contains(int key)`, `boolean delete(int key)` returning `true` iff the key existed, `List<Integer> inorder()` returning keys in ascending order, and `int size()`. `delete` must correctly handle the leaf, single-child, and two-children (replace with in-order successor or predecessor and remove that successor) cases.

## Rubric

- **Correctness (40)** — All five methods behave per the spec. `insert` is idempotent on duplicates. `delete` correctly handles leaf, single-child, and two-children cases (replace with in-order successor or predecessor and remove that successor afterwards). `inorder` returns keys in ascending order. `contains` and `size` are correct. No NullPointerException on contains/delete of missing keys. The code compiles.
- **Data Structures (30)** — A genuine BST with `Node { key, left, right }` honouring the BST invariant. `Node` is a private inner class with private fields (encapsulated), not public. Does not delegate to `java.util.TreeSet` / `TreeMap` as a hidden cheat that defeats the spirit of the assignment. The chosen approach (recursive, iterative) is applied consistently across methods.
- **Efficiency (15)** — `size()` is O(1) (cached), not recomputed by walking the tree on every call. `inorder` does not concatenate strings or repeatedly resize a fixed-size array. Avoids stack overflow on long degenerate inputs, or the limitation is acknowledged.
- **Code Quality (15)** — Idiomatic Java. Uses `List<Integer>` (interface) rather than `ArrayList<Integer>` in return types. Methods have clear names and consistent recursion / iteration style.

## Score sheet

| Submission | Correctness (40) | Data Structures (30) | Efficiency (15) | Code Quality (15) | **Total** | Notes |
|---|---|---|---|---|---|---|
| BstA1 |      |      |      |      |        |       |
| BstA2 |      |      |      |      |        |       |
| BstA3 |      |      |      |      |        |       |
| BstB1 |      |      |      |      |        |       |
| BstB2 |      |      |      |      |        |       |
| BstB3 |      |      |      |      |        |       |
| BstC1 |      |      |      |      |        |       |
| BstC2 |      |      |      |      |        |       |
| BstD1 |      |      |      |      |        |       |
| BstD2 |      |      |      |      |        |       |
| BstE1 |      |      |      |      |        |       |
| BstE2 |      |      |      |      |        |       |
| BstE3 |      |      |      |      |        |       |
| BstE4 |      |      |      |      |        |       |
| BstF1 |      |      |      |      |        |       |
| BstF2 |      |      |      |      |        |       |
| BstF3 |      |      |      |      |        |       |
| BstG1 |      |      |      |      |        |       |
| BstG2 |      |      |      |      |        |       |
| BstH1 |      |      |      |      |        |       |
| BstH2 |      |      |      |      |        |       |
| BstI1 |      |      |      |      |        |       |
| BstI2 |      |      |      |      |        |       |

## Submissions

### 1. `BstA1`

```java
import java.util.ArrayList;
import java.util.List;

public class BstA1 {
    public class Node {
        public int key;
        public Node left, right;
        public Node(int k) { this.key = k; }
    }

    public Node root;
    public int n = 0;

    public void insert(int key) {
        root = ins(root, key);
    }
    private Node ins(Node t, int k) {
        if (t == null) { n++; return new Node(k); }
        if (k < t.key) t.left = ins(t.left, k);
        else if (k > t.key) t.right = ins(t.right, k);
        return t;
    }

    public boolean contains(int key) {
        Node t = root;
        while (t != null) {
            if (key == t.key) return true;
            t = key < t.key ? t.left : t.right;
        }
        return false;
    }

    public boolean delete(int key) {
        if (!contains(key)) return false;
        root = del(root, key);
        n--;
        return true;
    }
    private Node del(Node t, int k) {
        if (t == null) return null;
        if (k < t.key) { t.left = del(t.left, k); return t; }
        if (k > t.key) { t.right = del(t.right, k); return t; }
        if (t.left == null) return t.right;
        if (t.right == null) return t.left;
        Node s = t.right;
        while (s.left != null) s = s.left;
        t.key = s.key;
        t.right = del(t.right, s.key);
        return t;
    }

    public List<Integer> inorder() {
        List<Integer> out = new ArrayList<>();
        in(root, out);
        return out;
    }
    private void in(Node t, List<Integer> out) {
        if (t == null) return;
        in(t.left, out);
        System.out.println(t.key);
        out.add(t.key);
        in(t.right, out);
    }

    public int size() { return n; }
}
```

> Correctness: ____/40  Data Structures: ____/30  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 2. `BstA2`

```java
import java.util.ArrayList;
import java.util.List;

public class BstA2 {
    private static class Node {
        int key;
        Node left, right;
        Node(int k) { this.key = k; }
    }

    private Node root;
    private int count = 0;

    public void insert(int key) {
        if (!contains(key)) {
            root = insertRec(root, key);
            count++;
        }
    }

    private Node insertRec(Node node, int key) {
        if (node == null) return new Node(key);
        if (key < node.key) node.left = insertRec(node.left, key);
        else if (key > node.key) node.right = insertRec(node.right, key);
        return node;
    }

    public boolean contains(int key) {
        return containsRec(root, key);
    }

    private boolean containsRec(Node node, int key) {
        if (node == null) return false;
        if (key == node.key) return true;
        if (key < node.key) return containsRec(node.left, key);
        return containsRec(node.right, key);
    }

    public boolean delete(int key) {
        if (!contains(key)) return false;
        root = deleteRec(root, key);
        count--;
        return true;
    }

    private Node deleteRec(Node node, int key) {
        if (node == null) return null;
        if (key < node.key) node.left = deleteRec(node.left, key);
        else if (key > node.key) node.right = deleteRec(node.right, key);
        else {
            if (node.left == null) return node.right;
            if (node.right == null) return node.left;
            Node succ = node.right;
            while (succ.left != null) succ = succ.left;
            node.key = succ.key;
            node.right = deleteRec(node.right, succ.key);
        }
        return node;
    }

    public List<Integer> inorder() {
        List<Integer> result = new ArrayList<>();
        inorderRec(root, result);
        return result;
    }

    private void inorderRec(Node node, List<Integer> out) {
        if (node == null) return;
        inorderRec(node.left, out);
        out.add(node.key);
        inorderRec(node.right, out);
    }

    public int size() { return count; }
}
```

> Correctness: ____/40  Data Structures: ____/30  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 3. `BstA3`

```java
import java.util.ArrayList;
import java.util.List;

public class BstA3 {

    private static final class Node {
        final int key;
        Node left;
        Node right;
        Node(int key) { this.key = key; }
    }

    private Node root;
    private int size;

    public void insert(int key) {
        int before = size;
        root = insert(root, key);
        if (size == before) {
            // duplicate — no change
        }
    }

    private Node insert(Node node, int key) {
        if (node == null) {
            size++;
            return new Node(key);
        }
        if (key < node.key)      node.left  = insert(node.left, key);
        else if (key > node.key) node.right = insert(node.right, key);
        return node;
    }

    public boolean contains(int key) {
        return find(root, key) != null;
    }

    private Node find(Node node, int key) {
        if (node == null || node.key == key) return node;
        return key < node.key ? find(node.left, key) : find(node.right, key);
    }

    public boolean delete(int key) {
        if (!contains(key)) return false;
        root = delete(root, key);
        size--;
        return true;
    }

    private Node delete(Node node, int key) {
        if (node == null) return null;
        if (key < node.key) {
            node.left = delete(node.left, key);
            return node;
        }
        if (key > node.key) {
            node.right = delete(node.right, key);
            return node;
        }
        if (node.left == null)  return node.right;
        if (node.right == null) return node.left;
        Node successor = leftmost(node.right);
        Node replacement = new Node(successor.key);
        replacement.left  = node.left;
        replacement.right = delete(node.right, successor.key);
        return replacement;
    }

    private Node leftmost(Node node) {
        while (node.left != null) node = node.left;
        return node;
    }

    public List<Integer> inorder() {
        List<Integer> out = new ArrayList<>();
        inorder(root, out);
        return out;
    }

    private void inorder(Node node, List<Integer> out) {
        if (node == null) return;
        inorder(node.left, out);
        out.add(node.key);
        inorder(node.right, out);
    }

    public int size() { return size; }
}
```

> Correctness: ____/40  Data Structures: ____/30  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 4. `BstB1`

```java
import java.util.ArrayList;
import java.util.List;

public class BstB1 {
    static class Node {
        public int key;
        public Node left;
        public Node right;
        Node(int k) { this.key = k; }
    }

    Node root;
    int n = 0;

    public void insert(int key) {
        if (root == null) { root = new Node(key); n++; return; }
        Node cur = root;
        while (true) {
            if (key == cur.key) return;
            if (key < cur.key) {
                if (cur.left == null) { cur.left = new Node(key); n++; return; }
                cur = cur.left;
            } else {
                if (cur.right == null) { cur.right = new Node(key); n++; return; }
                cur = cur.right;
            }
        }
    }

    public boolean contains(int key) {
        Node cur = root;
        while (cur != null) {
            if (key == cur.key) return true;
            cur = key < cur.key ? cur.left : cur.right;
        }
        return false;
    }

    public boolean delete(int key) {
        if (!contains(key)) return false;
        root = del(root, key);
        n--;
        return true;
    }
    private Node del(Node t, int k) {
        if (t == null) return null;
        if (k < t.key) { t.left = del(t.left, k); return t; }
        if (k > t.key) { t.right = del(t.right, k); return t; }
        if (t.left == null) return t.right;
        if (t.right == null) return t.left;
        Node s = t.right;
        while (s.left != null) s = s.left;
        t.key = s.key;
        t.right = del(t.right, s.key);
        return t;
    }

    public List<Integer> inorder() {
        List<Integer> out = new ArrayList<>();
        inHelper(root, out);
        return out;
    }
    private void inHelper(Node t, List<Integer> out) {
        if (t == null) return;
        inHelper(t.left, out);
        out.add(t.key);
        inHelper(t.right, out);
    }

    public int size() { return n; }
}
```

> Correctness: ____/40  Data Structures: ____/30  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 5. `BstB2`

```java
import java.util.ArrayList;
import java.util.List;

public class BstB2 {
    private static class Node {
        int key;
        Node left, right;
        Node(int k) { this.key = k; }
    }

    private Node root;
    private int count = 0;

    public void insert(int key) {
        if (root == null) {
            root = new Node(key);
            count++;
            return;
        }
        Node cur = root;
        while (true) {
            if (key == cur.key) return;
            if (key < cur.key) {
                if (cur.left == null) { cur.left = new Node(key); count++; return; }
                cur = cur.left;
            } else {
                if (cur.right == null) { cur.right = new Node(key); count++; return; }
                cur = cur.right;
            }
        }
    }

    public boolean contains(int key) {
        Node cur = root;
        while (cur != null) {
            if (key == cur.key) return true;
            cur = key < cur.key ? cur.left : cur.right;
        }
        return false;
    }

    public boolean delete(int key) {
        if (!contains(key)) return false;
        root = deleteRec(root, key);
        count--;
        return true;
    }

    private Node deleteRec(Node node, int key) {
        if (node == null) return null;
        if (key < node.key)      node.left  = deleteRec(node.left, key);
        else if (key > node.key) node.right = deleteRec(node.right, key);
        else {
            if (node.left == null)  return node.right;
            if (node.right == null) return node.left;
            Node succ = node.right;
            while (succ.left != null) succ = succ.left;
            node.key = succ.key;
            node.right = deleteRec(node.right, succ.key);
        }
        return node;
    }

    public List<Integer> inorder() {
        List<Integer> out = new ArrayList<>();
        inorderRec(root, out);
        return out;
    }

    private void inorderRec(Node node, List<Integer> out) {
        if (node == null) return;
        inorderRec(node.left, out);
        out.add(node.key);
        inorderRec(node.right, out);
    }

    public int size() { return count; }
}
```

> Correctness: ____/40  Data Structures: ____/30  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 6. `BstB3`

```java
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;

public class BstB3 {

    private static final class Node {
        int key;
        Node left, right;
        Node(int key) { this.key = key; }
    }

    private Node root;
    private int size;

    public void insert(int key) {
        if (root == null) {
            root = new Node(key);
            size++;
            return;
        }
        Node cur = root;
        while (true) {
            if (key == cur.key) return;
            if (key < cur.key) {
                if (cur.left == null) {
                    cur.left = new Node(key);
                    size++;
                    return;
                }
                cur = cur.left;
            } else {
                if (cur.right == null) {
                    cur.right = new Node(key);
                    size++;
                    return;
                }
                cur = cur.right;
            }
        }
    }

    public boolean contains(int key) {
        Node cur = root;
        while (cur != null) {
            if (key == cur.key) return true;
            cur = key < cur.key ? cur.left : cur.right;
        }
        return false;
    }

    public boolean delete(int key) {
        Node parent = null;
        Node cur = root;
        while (cur != null && cur.key != key) {
            parent = cur;
            cur = key < cur.key ? cur.left : cur.right;
        }
        if (cur == null) return false;

        Node replacement = removeNode(cur);
        if (parent == null)             root = replacement;
        else if (parent.left == cur)    parent.left = replacement;
        else                            parent.right = replacement;
        size--;
        return true;
    }

    private Node removeNode(Node node) {
        if (node.left == null)  return node.right;
        if (node.right == null) return node.left;
        Node succParent = node;
        Node succ = node.right;
        while (succ.left != null) {
            succParent = succ;
            succ = succ.left;
        }
        node.key = succ.key;
        if (succParent == node) succParent.right = succ.right;
        else                    succParent.left  = succ.right;
        return node;
    }

    public List<Integer> inorder() {
        List<Integer> out = new ArrayList<>(size);
        Deque<Node> stack = new ArrayDeque<>();
        Node cur = root;
        while (cur != null || !stack.isEmpty()) {
            while (cur != null) {
                stack.push(cur);
                cur = cur.left;
            }
            cur = stack.pop();
            out.add(cur.key);
            cur = cur.right;
        }
        return out;
    }

    public int size() { return size; }
}
```

> Correctness: ____/40  Data Structures: ____/30  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 7. `BstC1`

```java
import java.util.ArrayList;
import java.util.List;

@SuppressWarnings({"rawtypes", "unchecked"})
public class BstC1<T extends Comparable<T>> {
    private static class Node {
        Comparable key;
        Node left, right;
        Node(Comparable k) { this.key = k; }
    }

    private Node root;
    private int n = 0;

    public void insert(T key) {
        root = ins(root, key);
    }
    private Node ins(Node t, Comparable k) {
        if (t == null) { n++; return new Node(k); }
        int c = k.compareTo(t.key);
        if (c < 0) t.left = ins(t.left, k);
        else if (c > 0) t.right = ins(t.right, k);
        return t;
    }

    public boolean contains(T key) {
        Node t = root;
        while (t != null) {
            int c = key.compareTo(t.key);
            if (c == 0) return true;
            t = c < 0 ? t.left : t.right;
        }
        return false;
    }

    public boolean delete(T key) {
        if (!contains(key)) return false;
        root = del(root, key);
        n--;
        return true;
    }
    private Node del(Node t, Comparable k) {
        if (t == null) return null;
        int c = k.compareTo(t.key);
        if (c < 0) { t.left = del(t.left, k); return t; }
        if (c > 0) { t.right = del(t.right, k); return t; }
        if (t.left == null) return t.right;
        if (t.right == null) return t.left;
        Node s = t.right;
        while (s.left != null) s = s.left;
        t.key = s.key;
        t.right = del(t.right, s.key);
        return t;
    }

    public List<T> inorder() {
        List<T> out = new ArrayList<>();
        in(root, out);
        return out;
    }
    private void in(Node t, List<T> out) {
        if (t == null) return;
        in(t.left, out);
        out.add((T) t.key);
        in(t.right, out);
    }

    public int size() { return n; }
}
```

> Correctness: ____/40  Data Structures: ____/30  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 8. `BstC2`

```java
import java.util.ArrayList;
import java.util.List;

public class BstC2<T extends Comparable<T>> {

    private final class Node {
        T key;
        Node left, right;
        Node(T key) { this.key = key; }
    }

    private Node root;
    private int size;

    public void insert(T key) {
        root = insert(root, key);
    }

    private Node insert(Node node, T key) {
        if (node == null) {
            size++;
            return new Node(key);
        }
        int cmp = key.compareTo(node.key);
        if (cmp < 0)      node.left  = insert(node.left, key);
        else if (cmp > 0) node.right = insert(node.right, key);
        return node;
    }

    public boolean contains(T key) {
        Node cur = root;
        while (cur != null) {
            int cmp = key.compareTo(cur.key);
            if (cmp == 0) return true;
            cur = cmp < 0 ? cur.left : cur.right;
        }
        return false;
    }

    public boolean delete(T key) {
        if (!contains(key)) return false;
        root = delete(root, key);
        size--;
        return true;
    }

    private Node delete(Node node, T key) {
        if (node == null) return null;
        int cmp = key.compareTo(node.key);
        if (cmp < 0) {
            node.left = delete(node.left, key);
            return node;
        }
        if (cmp > 0) {
            node.right = delete(node.right, key);
            return node;
        }
        if (node.left == null)  return node.right;
        if (node.right == null) return node.left;
        Node successor = leftmost(node.right);
        node.key = successor.key;
        node.right = delete(node.right, successor.key);
        return node;
    }

    private Node leftmost(Node node) {
        while (node.left != null) node = node.left;
        return node;
    }

    public List<T> inorder() {
        List<T> out = new ArrayList<>(size);
        inorder(root, out);
        return out;
    }

    private void inorder(Node node, List<T> out) {
        if (node == null) return;
        inorder(node.left, out);
        out.add(node.key);
        inorder(node.right, out);
    }

    public int size() { return size; }
}
```

> Correctness: ____/40  Data Structures: ____/30  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 9. `BstD1`

```java
import java.util.ArrayList;
import java.util.List;
import java.util.TreeSet;

public class BstD1 {
    private final TreeSet<Integer> set = new TreeSet<>();

    public void insert(int key) {
        set.add(key);
    }

    public boolean contains(int key) {
        return set.contains(key);
    }

    public boolean delete(int key) {
        return set.remove(key);
    }

    public List<Integer> inorder() {
        return new ArrayList<>(set);
    }

    public int size() {
        return set.size();
    }
}
```

> Correctness: ____/40  Data Structures: ____/30  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 10. `BstD2`

```java
import java.util.ArrayList;
import java.util.List;
import java.util.TreeMap;

public class BstD2 {
    private final TreeMap<Integer, Boolean> map = new TreeMap<>();

    public void insert(int key) {
        map.putIfAbsent(key, Boolean.TRUE);
    }

    public boolean contains(int key) {
        return map.containsKey(key);
    }

    public boolean delete(int key) {
        return map.remove(key) != null;
    }

    public List<Integer> inorder() {
        return new ArrayList<>(map.keySet());
    }

    public int size() {
        return map.size();
    }
}
```

> Correctness: ____/40  Data Structures: ____/30  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 11. `BstE1`

```java
import java.util.ArrayList;
import java.util.List;

public class BstE1 {
    private static class Node {
        int key;
        Node left, right;
        Node(int k) { this.key = k; }
    }

    private Node root;
    private int n = 0;

    public void insert(int key) {
        root = ins(root, key);
        n++;
    }
    private Node ins(Node t, int k) {
        if (t == null) return new Node(k);
        if (k < t.key) t.left = ins(t.left, k);
        else           t.right = ins(t.right, k);
        return t;
    }

    public boolean contains(int key) {
        Node t = root;
        while (t != null) {
            if (key == t.key) return true;
            t = key < t.key ? t.left : t.right;
        }
        return false;
    }

    public boolean delete(int key) {
        if (!contains(key)) return false;
        root = del(root, key);
        n--;
        return true;
    }
    private Node del(Node t, int k) {
        if (t == null) return null;
        if (k < t.key) { t.left = del(t.left, k); return t; }
        if (k > t.key) { t.right = del(t.right, k); return t; }
        if (t.left == null) return t.right;
        if (t.right == null) return t.left;
        Node s = t.right;
        while (s.left != null) s = s.left;
        t.key = s.key;
        t.right = del(t.right, s.key);
        return t;
    }

    public List<Integer> inorder() {
        List<Integer> out = new ArrayList<>();
        in(root, out);
        return out;
    }
    private void in(Node t, List<Integer> out) {
        if (t == null) return;
        in(t.left, out);
        out.add(t.key);
        in(t.right, out);
    }

    public int size() { return n; }
}
```

> Correctness: ____/40  Data Structures: ____/30  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 12. `BstE2`

```java
import java.util.ArrayList;
import java.util.List;

public class BstE2 {
    private static class Node {
        int key;
        Node left, right;
        Node(int k) { this.key = k; }
    }

    private Node root;
    private int n = 0;

    public void insert(int key) {
        root = ins(root, key);
    }
    private Node ins(Node t, int k) {
        if (t == null) { n++; return new Node(k); }
        if (k < t.key) t.left = ins(t.left, k);
        else if (k > t.key) t.right = ins(t.right, k);
        return t;
    }

    public boolean contains(int key) {
        return cont(root, key);
    }
    private boolean cont(Node t, int k) {
        if (root == null) return false;
        if (k == root.key) return true;
        if (k < root.key) return cont(root.left, k);
        return cont(root.right, k);
    }

    public boolean delete(int key) {
        if (!contains(key)) return false;
        root = del(root, key);
        n--;
        return true;
    }
    private Node del(Node t, int k) {
        if (t == null) return null;
        if (k < t.key) { t.left = del(t.left, k); return t; }
        if (k > t.key) { t.right = del(t.right, k); return t; }
        if (t.left == null) return t.right;
        if (t.right == null) return t.left;
        Node s = t.right;
        while (s.left != null) s = s.left;
        t.key = s.key;
        t.right = del(t.right, s.key);
        return t;
    }

    public List<Integer> inorder() {
        List<Integer> out = new ArrayList<>();
        in(root, out);
        return out;
    }
    private void in(Node t, List<Integer> out) {
        if (t == null) return;
        in(t.left, out);
        out.add(t.key);
        in(t.right, out);
    }

    public int size() { return n; }
}
```

> Correctness: ____/40  Data Structures: ____/30  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 13. `BstE3`

```java
import java.util.ArrayList;
import java.util.List;

public class BstE3 {
    private static class Node {
        int key;
        Node left, right;
        Node(int k) { this.key = k; }
    }

    private Node root;
    private int n = 0;

    public void insert(int key) {
        root = ins(root, key);
    }
    private Node ins(Node t, int k) {
        if (t == null) { n++; return new Node(k); }
        if (k < t.key) t.left = ins(t.left, k);
        else if (k > t.key) t.right = ins(t.right, k);
        return t;
    }

    public boolean contains(int key) {
        Node t = root;
        while (t != null) {
            if (key == t.key) return true;
            t = key < t.key ? t.left : t.right;
        }
        return false;
    }

    public boolean delete(int key) {
        if (!contains(key)) return false;
        root = del(root, key);
        n--;
        return true;
    }
    private Node del(Node t, int k) {
        if (t == null) return null;
        if (k < t.key) { t.left = del(t.left, k); return t; }
        if (k > t.key) { t.right = del(t.right, k); return t; }
        if (t.left == null) return t.right;
        if (t.right == null) return t.left;
        Node s = t.right;
        while (s.left != null) s = s.left;
        t.key = s.key;
        t.right = del(t.right, s.key);
        return t;
    }

    public List<Integer> inorder() {
        List<Integer> out = new ArrayList<>();
        preorder(root, out);
        return out;
    }
    private void preorder(Node t, List<Integer> out) {
        if (t == null) return;
        out.add(t.key);
        preorder(t.left, out);
        preorder(t.right, out);
    }

    public int size() { return n; }
}
```

> Correctness: ____/40  Data Structures: ____/30  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 14. `BstE4`

```java
import java.util.ArrayList;
import java.util.List;

public class BstE4 {
    private static class Node {
        int key;
        Node left, right;
        Node(int k) { this.key = k; }
    }

    private Node root;
    private int n = 0;

    public void insert(int key) {
        root = ins(root, key);
    }
    private Node ins(Node t, int k) {
        if (t == null) { n++; return new Node(k); }
        if (k < t.key) t.left = ins(t.left, k);
        else if (k > t.key) t.right = ins(t.right, k);
        return t;
    }

    public boolean contains(int key) {
        Node t = root;
        while (t != null) {
            if (key == t.key) return true;
            t = key < t.key ? t.left : t.right;
        }
        return false;
    }

    public boolean delete(int key) {
        if (!contains(key)) return false;
        root = del(root, key);
        n--;
        return true;
    }
    private Node del(Node t, int k) {
        if (t == null) return null;
        if (k < t.key) { t.left = del(t.left, k); return t; }
        if (k > t.key) { t.right = del(t.right, k); return t; }
        if (t.left == null) return t.right;
        if (t.right == null) return t.left;
        Node s = t.right;
        while (s.left != null) s = s.left;
        t.key = s.key;
        return t;
    }

    public List<Integer> inorder() {
        List<Integer> out = new ArrayList<>();
        in(root, out);
        return out;
    }
    private void in(Node t, List<Integer> out) {
        if (t == null) return;
        in(t.left, out);
        out.add(t.key);
        in(t.right, out);
    }

    public int size() { return n; }
}
```

> Correctness: ____/40  Data Structures: ____/30  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 15. `BstF1`

```java
import java.util.ArrayList;
import java.util.List;

public class BstF1 {
    private static class Node {
        int key;
        Node left, right;
        Node(int k) { this.key = k; }
    }

    private Node root;
    private int n = 0;

    public void insert(int key) {
        root = ins(root, key);
    }
    private Node ins(Node t, int k) {
        if (t == null) { n++; return new Node(k); }
        if (k < t.key) t.left = ins(t.left, k);
        else if (k > t.key) t.right = ins(t.right, k);
        return t;
    }

    public boolean contains(int key) {
        Node t = root;
        while (t != null) {
            if (key == t.key) return true;
            t = key < t.key ? t.left : t.right;
        }
        return false;
    }

    public boolean delete(int key) {
        if (!contains(key)) return false;
        if (root.key == key) {
            if (root.left == null && root.right == null) {
                root = null;
            }
            // forgot the case where root has children
            n--;
            return true;
        }
        root = del(root, key);
        n--;
        return true;
    }

    private Node del(Node t, int k) {
        if (t == null) return null;
        if (k < t.key) { t.left = del(t.left, k); return t; }
        if (k > t.key) { t.right = del(t.right, k); return t; }
        if (t.left == null) return t.right;
        if (t.right == null) return t.left;
        Node s = t.right;
        while (s.left != null) s = s.left;
        t.key = s.key;
        t.right = del(t.right, s.key);
        return t;
    }

    public List<Integer> inorder() {
        List<Integer> out = new ArrayList<>();
        in(root, out);
        return out;
    }
    private void in(Node t, List<Integer> out) {
        if (t == null) return;
        in(t.left, out);
        out.add(t.key);
        in(t.right, out);
    }

    public int size() { return n; }
}
```

> Correctness: ____/40  Data Structures: ____/30  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 16. `BstF2`

```java
import java.util.ArrayList;
import java.util.List;

public class BstF2 {
    private static class Node {
        int key;
        Node left, right;
        Node(int k) { this.key = k; }
    }

    private Node root;
    private int n = 0;

    public void insert(int key) {
        root = ins(root, key);
    }
    private Node ins(Node t, int k) {
        if (t == null) { n++; return new Node(k); }
        if (k < t.key) t.left = ins(t.left, k);
        else if (k > t.key) t.right = ins(t.right, k);
        return t;
    }

    public boolean contains(int key) {
        return cont(root, key);
    }
    private boolean cont(Node t, int k) {
        if (k == t.key) return true;
        if (k < t.key) return cont(t.left, k);
        return cont(t.right, k);
    }

    public boolean delete(int key) {
        if (!contains(key)) return false;
        root = del(root, key);
        n--;
        return true;
    }
    private Node del(Node t, int k) {
        if (t == null) return null;
        if (k < t.key) { t.left = del(t.left, k); return t; }
        if (k > t.key) { t.right = del(t.right, k); return t; }
        if (t.left == null) return t.right;
        if (t.right == null) return t.left;
        Node s = t.right;
        while (s.left != null) s = s.left;
        t.key = s.key;
        t.right = del(t.right, s.key);
        return t;
    }

    public List<Integer> inorder() {
        List<Integer> out = new ArrayList<>();
        in(root, out);
        return out;
    }
    private void in(Node t, List<Integer> out) {
        if (t == null) return;
        in(t.left, out);
        out.add(t.key);
        in(t.right, out);
    }

    public int size() { return n; }
}
```

> Correctness: ____/40  Data Structures: ____/30  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 17. `BstF3`

```java
import java.util.ArrayList;
import java.util.List;

public class BstF3 {
    private static class Node {
        int key;
        Node left, right;
        Node(int k) { this.key = k; }
    }

    private Node root;

    public void insert(int key) {
        root = ins(root, key);
    }
    private Node ins(Node t, int k) {
        if (t == null) return new Node(k);
        if (k < t.key) t.left = ins(t.left, k);
        else if (k > t.key) t.right = ins(t.right, k);
        return t;
    }

    public boolean contains(int key) {
        Node t = root;
        while (t != null) {
            if (key == t.key) return true;
            t = key < t.key ? t.left : t.right;
        }
        return false;
    }

    public boolean delete(int key) {
        if (!contains(key)) return false;
        root = del(root, key);
        return true;
    }
    private Node del(Node t, int k) {
        if (t == null) return null;
        if (k < t.key) { t.left = del(t.left, k); return t; }
        if (k > t.key) { t.right = del(t.right, k); return t; }
        if (t.left == null) return t.right;
        if (t.right == null) return t.left;
        Node s = t.right;
        while (s.left != null) s = s.left;
        t.key = s.key;
        t.right = del(t.right, s.key);
        return t;
    }

    public List<Integer> inorder() {
        List<Integer> out = new ArrayList<>();
        in(root, out);
        return out;
    }
    private void in(Node t, List<Integer> out) {
        if (t == null) return;
        in(t.left, out);
        out.add(t.key);
        in(t.right, out);
    }

    public int size() {
        return inorder().size();
    }
}
```

> Correctness: ____/40  Data Structures: ____/30  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 18. `BstG1`

```java
import java.util.ArrayList;
import java.util.List;

public class BstG1 {
    private static class Node {
        int key;
        Node left, right;
        Node(int k) { this.key = k; }
    }

    private Node root;
    private int n = 0;

    public void insert(int key) {
        root = ins(root, key);
    }
    private Node ins(Node t, int k) {
        if (t == null) { n++; return new Node(k); }
        if (k < t.key) t.left = ins(t.left, k);
        else if (k > t.key) t.right = ins(t.right, k);
        return t;
    }

    public boolean contains(int key) {
        return cont(root, key);
    }
    private boolean cont(Node t, int k) {
        if (t == null) return false;
        if (k == t.key) return true;
        if (k < t.key) return cont(t.left, k);
        return cont(t.right, k);
    }

    public boolean delete(int key) {
        if (!contains(key)) return false;
        root = del(root, key);
        n--;
        return true;
    }
    private Node del(Node t, int k) {
        if (t == null) return null;
        if (k < t.key) { t.left = del(t.left, k); return t; }
        if (k > t.key) { t.right = del(t.right, k); return t; }
        if (t.left == null) return t.right;
        if (t.right == null) return t.left;
        Node s = t.right;
        while (s.left != null) s = s.left;
        t.key = s.key;
        t.right = del(t.right, s.key);
        return t;
    }

    public List<Integer> inorder() {
        List<Integer> out = new ArrayList<>();
        in(root, out);
        return out;
    }
    private void in(Node t, List<Integer> out) {
        if (t == null) return;
        in(t.left, out);
        out.add(t.key);
        in(t.right, out);
    }

    public int size() { return n; }
}
```

> Correctness: ____/40  Data Structures: ____/30  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 19. `BstG2`

```java
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

public class BstG2 {
    private static class Node {
        int key;
        Node left, right;
        Node(int k) { this.key = k; }
    }

    private Node root;
    private int n = 0;

    public void insert(int key) {
        root = ins(root, key);
    }
    private Node ins(Node t, int k) {
        if (t == null) { n++; return new Node(k); }
        if (k < t.key) t.left = ins(t.left, k);
        else if (k > t.key) t.right = ins(t.right, k);
        return t;
    }

    public boolean contains(int key) {
        Node t = root;
        while (t != null) {
            if (key == t.key) return true;
            t = key < t.key ? t.left : t.right;
        }
        return false;
    }

    public boolean delete(int key) {
        if (!contains(key)) return false;
        root = del(root, key);
        n--;
        return true;
    }
    private Node del(Node t, int k) {
        if (t == null) return null;
        if (k < t.key) { t.left = del(t.left, k); return t; }
        if (k > t.key) { t.right = del(t.right, k); return t; }
        if (t.left == null) return t.right;
        if (t.right == null) return t.left;
        Node s = t.right;
        while (s.left != null) s = s.left;
        t.key = s.key;
        t.right = del(t.right, s.key);
        return t;
    }

    public List<Integer> inorder() {
        String s = build(root);
        if (s.isEmpty()) return new ArrayList<>();
        return Arrays.stream(s.split(","))
                .map(String::trim)
                .filter(x -> !x.isEmpty())
                .map(Integer::parseInt)
                .collect(Collectors.toList());
    }
    private String build(Node t) {
        if (t == null) return "";
        return build(t.left) + ", " + t.key + build(t.right);
    }

    public int size() { return n; }
}
```

> Correctness: ____/40  Data Structures: ____/30  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 20. `BstH1`

```java
import java.util.ArrayList;
import java.util.List;

public class BstH1 {
    private class Node {
        int key;
        Node left, right;
        Node(int k) { this.key = k; }
    }

    private static Node root;
    private int n = 0;

    public void insert(int key) {
        root = ins(root, key);
    }
    private Node ins(Node t, int k) {
        if (t == null) { n++; return new Node(k); }
        if (k < t.key) t.left = ins(t.left, k);
        else if (k > t.key) t.right = ins(t.right, k);
        return t;
    }

    public boolean contains(int key) {
        Node t = root;
        while (t != null) {
            if (key == t.key) return true;
            t = key < t.key ? t.left : t.right;
        }
        return false;
    }

    public boolean delete(int key) {
        return false;
    }

    public List<Integer> inorder() {
        return new ArrayList<>();
    }

    public int size() { return n; }
}
```

> Correctness: ____/40  Data Structures: ____/30  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 21. `BstH2`

```java
import java.util.ArrayList;

public class BstH2 {
    private static class Node {
        int key;
        Node left, right;
        Node(int k) { this.key = k; }
    }

    private Node root;
    private int n = 0;

    public void insert(int key) {
        root = ins(root, key);
    }
    private Node ins(Node t, int k) {
        if (t == null) { n++; return new Node(k); }
        if (k < t.key) t.left = ins(t.left, k);
        else if (k > t.key) t.right = ins(t.right, k);
        return t;
    }

    public boolean contains(int key) {
        Node t = root;
        while (t != null) {
            if (key == t.key) return true;
            t = key < t.key ? t.left : t.right;
        }
        return false;
    }

    public boolean delete(int key) {
        return false;
    }

    public List<Integer> inorder() {
        return new ArrayList<>();
    }

    public int size() { return n; }
}
```

> Correctness: ____/40  Data Structures: ____/30  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 22. `BstI1`

```java
import java.util.ArrayList;
import java.util.List;

public class BstI1 {

    private static final class Node {
        int key;
        int subtreeSize;
        Node left, right;
        Node(int key) { this.key = key; this.subtreeSize = 1; }
    }

    private Node root;

    public void insert(int key) {
        root = insert(root, key);
    }

    private Node insert(Node node, int key) {
        if (node == null) return new Node(key);
        if (key < node.key)      node.left  = insert(node.left, key);
        else if (key > node.key) node.right = insert(node.right, key);
        else                     return node;
        node.subtreeSize = 1 + size(node.left) + size(node.right);
        return node;
    }

    public boolean contains(int key) {
        Node cur = root;
        while (cur != null) {
            if (key == cur.key) return true;
            cur = key < cur.key ? cur.left : cur.right;
        }
        return false;
    }

    public boolean delete(int key) {
        if (!contains(key)) return false;
        root = delete(root, key);
        return true;
    }

    private Node delete(Node node, int key) {
        if (node == null) return null;
        if (key < node.key) {
            node.left = delete(node.left, key);
        } else if (key > node.key) {
            node.right = delete(node.right, key);
        } else {
            if (node.left == null)  return node.right;
            if (node.right == null) return node.left;
            Node succ = node.right;
            while (succ.left != null) succ = succ.left;
            node.key = succ.key;
            node.right = delete(node.right, succ.key);
        }
        node.subtreeSize = 1 + size(node.left) + size(node.right);
        return node;
    }

    public List<Integer> inorder() {
        List<Integer> out = new ArrayList<>(size());
        inorder(root, out);
        return out;
    }

    private void inorder(Node node, List<Integer> out) {
        if (node == null) return;
        inorder(node.left, out);
        out.add(node.key);
        inorder(node.right, out);
    }

    public int size() {
        return size(root);
    }

    private int size(Node node) {
        return node == null ? 0 : node.subtreeSize;
    }
}
```

> Correctness: ____/40  Data Structures: ____/30  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:

### 23. `BstI2`

```java
import java.util.ArrayList;
import java.util.List;

public class BstI2 {

    private static final class Node {
        int key;
        Node left, right;
        Node(int key) { this.key = key; }
    }

    private Node root;
    private int size;

    public void insert(int key) {
        root = insert(root, key);
    }

    private Node insert(Node node, int key) {
        if (node == null) { size++; return new Node(key); }
        if (key < node.key)      node.left  = insert(node.left, key);
        else if (key > node.key) node.right = insert(node.right, key);
        return node;
    }

    public boolean contains(int key) {
        Node cur = root;
        while (cur != null) {
            if (key == cur.key) return true;
            cur = key < cur.key ? cur.left : cur.right;
        }
        return false;
    }

    public boolean delete(int key) {
        if (!contains(key)) return false;
        root = delete(root, key);
        size--;
        return true;
    }

    private Node delete(Node node, int key) {
        if (node == null) return null;
        if (key < node.key) {
            node.left = delete(node.left, key);
            return node;
        }
        if (key > node.key) {
            node.right = delete(node.right, key);
            return node;
        }
        if (node.left == null)  return node.right;
        if (node.right == null) return node.left;
        Node succ = node.right;
        while (succ.left != null) succ = succ.left;
        node.key = succ.key;
        node.right = delete(node.right, succ.key);
        return node;
    }

    public List<Integer> inorder() {
        List<Integer> out = new ArrayList<>(size);
        Node cur = root;
        while (cur != null) {
            if (cur.left == null) {
                out.add(cur.key);
                cur = cur.right;
            } else {
                Node pred = cur.left;
                while (pred.right != null && pred.right != cur) pred = pred.right;
                if (pred.right == null) {
                    pred.right = cur;
                    cur = cur.left;
                } else {
                    pred.right = null;
                    out.add(cur.key);
                    cur = cur.right;
                }
            }
        }
        return out;
    }

    public int size() { return size; }
}
```

> Correctness: ____/40  Data Structures: ____/30  Efficiency: ____/15  Code Quality: ____/15  →  **Total: ____/100**
>
> Notes:
