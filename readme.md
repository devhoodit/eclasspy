# Eclass api for python

## features

1. get attend info list
2. get subject info list
3. get lecture material list

## How to use
### Clone repository
```
git clone https://github.com/devhoodit/eclasspy
```

### Dependency
```
requests
bs4
```

## Examples

### Make instance
```python
import eclass
ec = eclass.login("your_id", "your_password")
```

### Get subject list
```python
print(ec.get_subjects()) # get all subjects list
```

### Get attend list
```python
print(ec.get_all_attend()) # get all attend list
```

### Get assignment list
```python
print(ec.get_all_assignment()) # get all assignment list
print(ec.get_all_assignment("subject_ky")) # get subject's assignment list
```

### Get notice list
```python
print(ec.get_all_notice()) # get all notice list
print(ec.get_notice("subject_ky")) # get subject's notice list
```

### Download lecture materials
```python
ec.download_all_lecture_materials("custom_path, default is current directory") # to path, download all subject's lecture materials (make each subject folder)
# or
ec.download_lecture_material("basepath", "subject_ky") # to basepath, download subject's lecture materials
```

Ref [dw_lecture_ex.py](https://github.com/devhoodit/eclasspy/blob/main/dw_lecture_ex.py)