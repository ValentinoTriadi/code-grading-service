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
