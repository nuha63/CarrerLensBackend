import re

with open(r'e:\Flutter\Carrer_Lens\career_lens_flutter\lib\models\roadmap_template_engine.dart', 'r', encoding='utf-8') as f:
    content = f.read()

def repl(match):
    skills = match.group(1).split(', ')
    new_skills = []
    for i, s in enumerate(skills):
        s = s.strip()
        if not s: continue
        # s is like 'Dart' (with quotes)
        # extract the text
        val = s.strip("'")
        new_skills.append(f"RoadmapSkill(id: 'template_skill_{i}', skillName: '{val}')")
    
    return f"keySkills: [{', '.join(new_skills)}],"

content = re.sub(r"keySkills:\s*\[(.*?)\]\s*,", repl, content)

with open(r'e:\Flutter\Carrer_Lens\career_lens_flutter\lib\models\roadmap_template_engine.dart', 'w', encoding='utf-8') as f:
    f.write(content)
