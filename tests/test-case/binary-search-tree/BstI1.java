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
