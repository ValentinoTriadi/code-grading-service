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
