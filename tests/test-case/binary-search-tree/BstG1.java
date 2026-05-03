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
