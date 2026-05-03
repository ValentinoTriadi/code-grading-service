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
