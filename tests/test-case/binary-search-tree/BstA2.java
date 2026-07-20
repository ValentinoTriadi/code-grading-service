import java.util.ArrayList;
import java.util.List;

public class BstA2 {
    private static class Node {
        int key;
        Node left, right;
        Node(int k) { this.key = k; }
    }

    private Node root;
    private int count = 0;

    public void insert(int key) {
        if (!contains(key)) {
            root = insertRec(root, key);
            count++;
        }
    }

    private Node insertRec(Node node, int key) {
        if (node == null) return new Node(key);
        if (key < node.key) node.left = insertRec(node.left, key);
        else if (key > node.key) node.right = insertRec(node.right, key);
        return node;
    }

    public boolean contains(int key) {
        return containsRec(root, key);
    }

    private boolean containsRec(Node node, int key) {
        if (node == null) return false;
        if (key == node.key) return true;
        if (key < node.key) return containsRec(node.left, key);
        return containsRec(node.right, key);
    }

    public boolean delete(int key) {
        if (!contains(key)) return false;
        root = deleteRec(root, key);
        count--;
        return true;
    }

    private Node deleteRec(Node node, int key) {
        if (node == null) return null;
        if (key < node.key) node.left = deleteRec(node.left, key);
        else if (key > node.key) node.right = deleteRec(node.right, key);
        else {
            if (node.left == null) return node.right;
            if (node.right == null) return node.left;
            Node succ = node.right;
            while (succ.left != null) succ = succ.left;
            node.key = succ.key;
            node.right = deleteRec(node.right, succ.key);
        }
        return node;
    }

    public List<Integer> inorder() {
        List<Integer> result = new ArrayList<>();
        inorderRec(root, result);
        return result;
    }

    private void inorderRec(Node node, List<Integer> out) {
        if (node == null) return;
        inorderRec(node.left, out);
        out.add(node.key);
        inorderRec(node.right, out);
    }

    public int size() { return count; }
}
