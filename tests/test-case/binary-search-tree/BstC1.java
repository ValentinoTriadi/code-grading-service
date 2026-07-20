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
