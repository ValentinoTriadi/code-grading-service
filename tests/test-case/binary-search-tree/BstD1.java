import java.util.ArrayList;
import java.util.List;
import java.util.TreeSet;

public class BstD1 {
    private final TreeSet<Integer> set = new TreeSet<>();

    public void insert(int key) {
        set.add(key);
    }

    public boolean contains(int key) {
        return set.contains(key);
    }

    public boolean delete(int key) {
        return set.remove(key);
    }

    public List<Integer> inorder() {
        return new ArrayList<>(set);
    }

    public int size() {
        return set.size();
    }
}
