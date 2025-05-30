from flask import Blueprint, Response, current_app
from app.models.experiences import Experience
from app.models.destinations import Destinations
from app import db
from datetime import datetime
import xml.etree.ElementTree as ET

sitemap_blueprint = Blueprint('sitemap', __name__)

@sitemap_blueprint.route('/sitemap.xml')
def dynamic_sitemap():
    """
    Route sitemap động - TỰ ĐỘNG cập nhật mỗi khi được gọi
    Hoạt động:
    1. User/GoogleBot truy cập yoursite.com/sitemap.xml
    2. Flask gọi hàm này
    3. Hàm đọc database và tạo sitemap mới
    4. Trả về XML cho client
    """
    try:
        # Tạo root element
        urlset = ET.Element('urlset')
        urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')

        base_url = 'https://dulichbyai.id.vn'  # Thay bằng domain thật
        
        # 1. STATIC PAGES
        static_pages = [
            {'url': '/', 'priority': '1.0', 'changefreq': 'daily'},
            {'url': '/page2', 'priority': '0.8', 'changefreq': 'weekly'},
            {'url': '/page3', 'priority': '0.8', 'changefreq': 'weekly'},
            {'url': '/page4', 'priority': '0.8', 'changefreq': 'weekly'},
            {'url': '/schedule', 'priority': '0.8', 'changefreq': 'weekly'},
            {'url': '/map', 'priority': '0.7', 'changefreq': 'weekly'},
            {'url': '/experiences', 'priority': '0.9', 'changefreq': 'daily'},
            {'url': '/share-experience', 'priority': '0.7', 'changefreq': 'weekly'},
            {'url': '/login', 'priority': '0.6', 'changefreq': 'monthly'},
            {'url': '/register', 'priority': '0.6', 'changefreq': 'monthly'},
            {'url': '/feedback', 'priority': '0.5', 'changefreq': 'monthly'},
        ]
        
        # Thêm static pages
        for page in static_pages:
            add_url_to_sitemap(urlset, base_url + page['url'], 
                             datetime.now(), page['changefreq'], page['priority'])
        
        # 2. DYNAMIC PAGES từ database
        
        # A. Tất cả experiences đã được approve
        experiences = Experience.query.filter_by(is_approved=True).all()
        current_app.logger.info(f"Found {len(experiences)} approved experiences")
        
        for exp in experiences:
            url = f"{base_url}/experience/{exp.id}"
            lastmod = exp.updated_at if exp.updated_at else exp.created_at
            
            # Priority dựa trên popularity
            views = exp.views or 0
            likes = exp.likes or 0
            popularity_score = views * 0.1 + likes * 0.2
            
            if popularity_score > 100:
                priority = '0.8'
            elif popularity_score > 50:
                priority = '0.7'
            else:
                priority = '0.6'
            
            add_url_to_sitemap(urlset, url, lastmod, 'monthly', priority)
        
        # B. Các tỉnh/điểm đến
        try:
            # Lấy destinations từ database
            destinations = db.session.query(Destinations.name).distinct().limit(50).all()
            current_app.logger.info(f"Found {len(destinations)} destinations")
            
            for dest in destinations:
                if dest.name and dest.name.strip():
                    province_slug = dest.name.lower().replace(' ', '-').replace(',', '')
                    url = f"{base_url}/page3?province={province_slug}"
                    add_url_to_sitemap(urlset, url, datetime.now(), 'weekly', '0.7')
                    
        except Exception as e:
            current_app.logger.error(f"Error loading destinations: {e}")
        
        # Tạo XML response
        tree = ET.ElementTree(urlset)
        ET.indent(tree, space="  ", level=0)
        
        xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml_str += ET.tostring(urlset, encoding='unicode')
        
        # Trả về response với proper headers
        response = Response(xml_str, mimetype='application/xml')
        response.headers['Content-Type'] = 'application/xml; charset=utf-8'
        response.headers['Cache-Control'] = 'public, max-age=3600'  # Cache 1 giờ
        
        current_app.logger.info("Sitemap generated successfully")
        return response
        
    except Exception as e:
        current_app.logger.error(f"Error generating sitemap: {e}")
        # Trả về sitemap cơ bản nếu có lỗi
        return generate_basic_sitemap()

def add_url_to_sitemap(urlset, url, lastmod, changefreq, priority):
    """Helper function để thêm URL vào sitemap"""
    url_elem = ET.SubElement(urlset, 'url')
    
    loc = ET.SubElement(url_elem, 'loc')
    loc.text = url
    
    lastmod_elem = ET.SubElement(url_elem, 'lastmod')
    if isinstance(lastmod, datetime):
        lastmod_elem.text = lastmod.strftime('%Y-%m-%d')
    else:
        lastmod_elem.text = str(lastmod)
    
    changefreq_elem = ET.SubElement(url_elem, 'changefreq')
    changefreq_elem.text = changefreq
    
    priority_elem = ET.SubElement(url_elem, 'priority')
    priority_elem.text = priority

def generate_basic_sitemap():
    """Sitemap cơ bản khi có lỗi"""
    basic_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://dulichbyai.id.vn/</loc>
    <lastmod>{}</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>'''.format(datetime.now().strftime('%Y-%m-%d'))
    
    response = Response(basic_xml, mimetype='application/xml')
    response.headers['Content-Type'] = 'application/xml; charset=utf-8'
    return response 