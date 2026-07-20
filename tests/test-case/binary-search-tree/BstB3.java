import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;

public class BstB3 {

    private static final class Node {
        int key;
        Node left, right;
        Node(int key) { this.key = key; }
    }

    private Node root;
    private int size;

    public void insert(int key) {
        if (root == null) {
            root = new Node(key);
            size++;
            return;
        }
        Node cur = root;
        while (true) {
            if (key == cur.key) return;
            if (key < cur.key) {
                if (cur.left == null) {
                    cur.left = new Node(key);
                    size++;
                    return;
                }
                cur = cur.left;
            } else {
                if (cur.right == null) {
                    cur.right = new Node(key);
                    size++;
                    return;
                }
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
        Node parent = null;
        Node cur = root;
        while (cur != null && cur.key != key) {
            parent = cur;
            cur = key < cur.key ? cur.left : cur.right;
        }
        if (cur == null) return false;

        Node replacement = removeNode(cur);
        if (parent == null)             root = replacement;
        else if (parent.left == cur)    parent.left = replacement;
        else                            parent.right = replacement;
        size--;
        return true;
    }

    private Node removeNode(Node node) {
        if (node.left == null)  return node.right;
        if (node.right == null) return node.left;
        Node succParent = node;
        Node succ = node.right;
        while (succ.left != null) {
            succParent = succ;
            succ = succ.left;
        }
        node.key = succ.key;
        if (succParent == node) succParent.right = succ.right;
        else                    succParent.left  = succ.right;
        return node;
    }

    public List<Integer> inorder() {
        List<Integer> out = new ArrayList<>(size);
        Deque<Node> stack = new ArrayDeque<>();
        Node cur = root;
        while (cur != null || !stack.isEmpty()) {
            while (cur != null) {
                stack.push(cur);
                cur = cur.left;
            }
            cur = stack.pop();
            out.add(cur.key);
            cur = cur.right;
        }
        return out;
    }

    public int size() { return size; }
}
