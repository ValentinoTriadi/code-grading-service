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
