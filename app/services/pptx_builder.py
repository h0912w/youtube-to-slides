from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

from app.utils.helpers import sanitize_text


def create_pptx(slides_data: list[dict], video_title: str, output_path: str) -> str:
    """PPT 파일 생성 후 저장 경로 반환."""
    prs = Presentation()

    # 슬라이드 크기: 13.333 x 7.5 인치 (와이드스크린)
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # --- 표지 슬라이드 ---
    blank_layout = prs.slide_layouts[6]  # 빈 레이아웃
    cover_slide = prs.slides.add_slide(blank_layout)

    # 다크 배경 (#1A1A2E)
    background = cover_slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = RGBColor(0x1A, 0x1A, 0x2E)

    # 제목 텍스트 박스 (중앙 배치)
    left = Inches(1)
    top = Inches(2.5)
    width = Inches(11.333)
    height = Inches(2.5)
    txBox = cover_slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = sanitize_text(video_title)
    run.font.size = Pt(40)
    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    run.font.bold = True

    # --- 내용 슬라이드 ---
    for slide_dict in slides_data:
        slide_title = sanitize_text(slide_dict.get("title", ""))
        bullets = slide_dict.get("bullets", [])

        content_slide = prs.slides.add_slide(blank_layout)

        # 흰색 배경
        bg = content_slide.background
        bg_fill = bg.fill
        bg_fill.solid()
        bg_fill.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

        # 제목 텍스트 박스
        title_left = Inches(0.5)
        title_top = Inches(0.4)
        title_width = Inches(12.333)
        title_height = Inches(1.0)
        title_box = content_slide.shapes.add_textbox(title_left, title_top, title_width, title_height)
        title_tf = title_box.text_frame
        title_tf.word_wrap = True

        title_para = title_tf.paragraphs[0]
        title_run = title_para.add_run()
        title_run.text = slide_title
        title_run.font.size = Pt(28)
        title_run.font.color.rgb = RGBColor(0x1A, 0x1A, 0x2E)
        title_run.font.bold = True

        # 파란 구분선 (#4444CC) - 얇은 직사각형으로 표현
        line_left = Inches(0.5)
        line_top = Inches(1.5)
        line_width = Inches(12.333)
        line_height = Emu(50000)  # 약 0.055인치
        line_shape = content_slide.shapes.add_shape(
            1,  # MSO_SHAPE_TYPE.RECTANGLE
            line_left, line_top, line_width, line_height
        )
        line_shape.fill.solid()
        line_shape.fill.fore_color.rgb = RGBColor(0x44, 0x44, 0xCC)
        line_shape.line.fill.background()  # 선 없음

        # 불릿 텍스트 박스
        bullet_left = Inches(0.5)
        bullet_top = Inches(1.7)
        bullet_width = Inches(12.333)
        bullet_height = Inches(5.5)
        bullet_box = content_slide.shapes.add_textbox(bullet_left, bullet_top, bullet_width, bullet_height)
        bullet_tf = bullet_box.text_frame
        bullet_tf.word_wrap = True

        for i, bullet_text in enumerate(bullets):
            if i == 0:
                para = bullet_tf.paragraphs[0]
            else:
                para = bullet_tf.add_paragraph()

            para.space_before = Pt(6)
            run = para.add_run()
            run.text = "• " + sanitize_text(bullet_text)
            run.font.size = Pt(18)
            run.font.color.rgb = RGBColor(0x33, 0x33, 0x33)

    prs.save(output_path)
    return output_path
