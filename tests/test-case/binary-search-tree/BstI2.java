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
