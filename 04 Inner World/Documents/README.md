# Documents

One markdown note per important document: the note carries the
metadata (what it is, when issued, when it expires, how much, who it
involves), the file itself lives in `05 Assets/Documents/` and is
linked via `source_file`.

Why two files? A PDF cannot carry properties. The note can - so the
note is the record and the binary is the attachment, per
[[GL-1002-frontmatter-conventions|GL-1002]] ("the wrapper-note
pattern") and [[GL-1006-bases-and-live-views|GL-1006]].

`Documents.base` in this folder shows everything as a sortable table
(and as cards once a document has a `preview_image`). Open it like
any note; edit properties right in the table.

The AI Team creates wrapper notes when documents are processed from
`01 Inbox/Scanner Inbox/`; ask and a scan becomes a findable record.
