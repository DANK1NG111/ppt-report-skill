"""OPC relationships and DrawingML invariants independent of PowerPoint UI."""
from collections import Counter
from pathlib import PurePosixPath
import posixpath
from zipfile import ZipFile,BadZipFile
from lxml import etree
from ppt_report_skill.models import Issue


def structural_issues(path):
    issues=[]
    try:
        with ZipFile(path) as archive:
            names=set(archive.namelist())
            if archive.testzip():issues.append(Issue('CORRUPT_ZIP','error','ZIP CRC 校验失败。'))
            for required in ['[Content_Types].xml','_rels/.rels','ppt/presentation.xml']:
                if required not in names:issues.append(Issue('INVALID_PPTX','error',f'缺少 {required}'))
            for name in names:
                if not name.endswith(('.xml','.rels')):continue
                try:root=etree.fromstring(archive.read(name))
                except etree.XMLSyntaxError as exc:
                    issues.append(Issue('INVALID_XML','error',f'{name}: {exc}'));continue
                if name.endswith('.rels'):
                    seen=set()
                    for rel in root:
                        rid=rel.get('Id')
                        if rid in seen:issues.append(Issue('DUPLICATE_RELATIONSHIP','error',f'{name} 重复关系 {rid}'))
                        seen.add(rid)
                        if rel.get('TargetMode')=='External':continue
                        target=rel.get('Target','').split('#',1)[0]
                        owner_dir=posixpath.dirname(posixpath.dirname(name))
                        resolved=posixpath.normpath(posixpath.join(owner_dir,target)) if not target.startswith('/') else target.lstrip('/')
                        if resolved not in names:issues.append(Issue('BROKEN_RELATIONSHIP','error',f'{name}: {target}'))
                else:
                    for node in root.iter():
                        counts=Counter(etree.QName(c).localname for c in node)
                        for tag in ['pPr','rPr','bodyPr','lstStyle']:
                            if counts[tag]>1:issues.append(Issue('DUPLICATE_XML_PROPERTY','error',f'{name}: {tag} 重复。'))
                    if name.startswith('ppt/slides/slide'):
                        ids=root.xpath('//*[local-name()="cNvPr"]/@id')
                        if len(ids)!=len(set(ids)):issues.append(Issue('DUPLICATE_SHAPE_ID','error',f'{name} 对象 ID 重复。'))
    except (BadZipFile,OSError) as exc:issues.append(Issue('INVALID_PPTX','error','文件不是可读的 PPTX：'+str(exc)))
    return issues
