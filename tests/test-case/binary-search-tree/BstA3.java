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
