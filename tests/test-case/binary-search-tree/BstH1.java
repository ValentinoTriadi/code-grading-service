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
