import { Plus, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { emptyTextItem, type TextItem } from "@/lib/grading-form"

interface Props {
  label: string
  items: TextItem[]
  placeholder?: string
  addLabel?: string
  onChange: (items: TextItem[]) => void
}

export function StringListEditor({
  label,
  items,
  placeholder,
  addLabel = "Add item",
  onChange,
}: Props) {
  function update(id: string, text: string) {
    onChange(items.map((it) => (it.id === id ? { ...it, text } : it)))
  }
  function remove(id: string) {
    onChange(items.filter((it) => it.id !== id))
  }
  function add() {
    onChange([...items, emptyTextItem()])
  }

  return (
    <div className="space-y-1.5">
      <Label className="text-xs">{label}</Label>
      {items.map((it) => (
        <div key={it.id} className="flex items-center gap-2">
          <Input
            placeholder={placeholder}
            value={it.text}
            onChange={(e) => update(it.id, e.target.value)}
          />
          <Button
            type="button"
            variant="ghost"
            size="icon-sm"
            onClick={() => remove(it.id)}
            aria-label="Remove"
          >
            <X />
          </Button>
        </div>
      ))}
      <Button type="button" variant="outline" size="xs" onClick={add}>
        <Plus /> {addLabel}
      </Button>
    </div>
  )
}
