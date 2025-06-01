from .. import db
from flask import url_for,request
import unicodedata  

class Destinations(db.Model):
    __tablename__ = "destinations"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    mood = db.Column(db.String(50), nullable=False)
    place = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)

    images = db.relationship('DestinationImage',back_populates = 'destination',cascade = "all, delete-orphan")

    def __init__(self, name, mood, place, location, description, image_url = None):
        self.name = name
        self.mood = mood
        self.place = place
        self.location = location
        self.description = description

class DestinationImage(db.Model):
    __tablename__ = "destination_images"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    destination_id = db.Column(db.Integer, db.ForeignKey('destinations.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)

    # 👇 Liên kết ngược về Destinations
    destination = db.relationship('Destinations', back_populates='images')

# Thêm dữ liệu mẫu khi app khởi động
def seed_destinations():
    if Destinations.query.first() is None:  # Kiểm tra xem đã có dữ liệu chưa
        sample_destinations = [
            # Các tỉnh đã có
                Destinations(
                    name="Hà Nội",
                    mood="active",
                    place="city",
                    location="north",
                    description="""Hà Nội, thủ đô của Việt Nam, là trung tâm chính trị, văn hóa, và kinh tế của cả nước, nằm ở khu vực Đồng bằng sông Hồng, phía Bắc Việt Nam. Với lịch sử hơn 1.000 năm, Hà Nội từng là kinh đô của nhiều triều đại phong kiến, nổi bật nhất là thời nhà Lý, Trần, và Lê. Thành phố này có nhiều di tích lịch sử nổi tiếng như Văn Miếu - Quốc Tử Giám, trường đại học đầu tiên của Việt Nam, và Hồ Hoàn Kiếm với tháp Rùa và đền Ngọc Sơn, biểu tượng của thủ đô. Hà Nội cũng là nơi tọa lạc của Lăng Chủ tịch Hồ Chí Minh, một địa điểm linh thiêng thu hút hàng triệu du khách. Về văn hóa, Hà Nội nổi tiếng với 36 phố phường cổ, nơi lưu giữ nét kiến trúc truyền thống và các làng nghề như làng gốm Bát Tràng, làng lụa Vạn Phúc. Khí hậu Hà Nội mang đặc trưng miền Bắc, với bốn mùa rõ rệt: mùa xuân mát mẻ, mùa hè nóng ẩm, mùa thu dịu dàng, và mùa đông lạnh. Ẩm thực Hà Nội là một điểm nhấn lớn, với các món như phở bò, bún chả, bánh cuốn Thanh Trì, và cốm làng Vòng. Hà Nội cũng là nơi tổ chức nhiều lễ hội truyền thống như lễ hội đền Cổ Loa, lễ hội Gióng, thu hút đông đảo du khách."""
                ),
                Destinations(
                    name="Hồ Chí Minh",
                    mood="active",
                    place="city",
                    location="south",
                    description="""Thành phố Hồ Chí Minh, thường được gọi là Sài Gòn, là trung tâm kinh tế, văn hóa, và chính trị lớn nhất của Việt Nam, nằm ở khu vực Đông Nam Bộ. Với diện tích khoảng 2.095 km², TP. HCM có dân số hơn 9 triệu người (theo thống kê năm 2023), nhưng con số thực tế có thể cao hơn do lượng người nhập cư lớn. Thành phố này được chia thành 22 quận, huyện và 1 thành phố trực thuộc (Thủ Đức), với các khu vực trung tâm như Quận 1, Quận 3 là nơi tập trung nhiều hoạt động thương mại và du lịch. TP. HCM nằm gần đồng bằng sông Cửu Long nhưng không thuộc khu vực này, được bao quanh bởi các tỉnh như Tây Ninh, Bình Dương, Đồng Nai, Bà Rịa - Vũng Tàu, và Long An. Địa hình TP. HCM tương đối bằng phẳng, với độ cao trung bình từ 5-10 mét so với mực nước biển, nhưng có một số khu vực như Quận 2 và Quận 7 được xây dựng trên vùng đất lấn biển. TP. HCM có khí hậu nhiệt đới gió mùa, chia thành hai mùa rõ rệt: mùa mưa (tháng 5 đến tháng 11) và mùa khô (tháng 12 đến tháng 4). Nhiệt độ trung bình dao động từ 27-35°C, với độ ẩm cao quanh năm, đặc biệt trong mùa mưa. TP. HCM có lịch sử phong phú, bắt đầu từ thời kỳ người Khmer sinh sống tại khu vực này, gọi là Prey Nokor, một cảng thương mại quan trọng. Đến thế kỷ 17, người Việt bắt đầu định cư và phát triển khu vực này. Năm 1698, Nguyễn Hữu Cảnh được Chúa Nguyễn cử vào Nam để thiết lập chính quyền, đánh dấu sự ra đời của Gia Định - tiền thân của TP. HCM. Trong thời kỳ Pháp thuộc, Sài Gòn được gọi là "Hòn ngọc Viễn Đông", là trung tâm kinh tế và văn hóa của Đông Dương. Sau năm 1975, Sài Gòn được đổi tên thành TP. Hồ Chí Minh để vinh danh Chủ tịch Hồ Chí Minh. Về văn hóa, TP. HCM là nơi giao thoa của nhiều nền văn hóa, với các di tích lịch sử như Dinh Độc Lập, Bảo tàng Chứng tích Chiến tranh, và Nhà thờ Đức Bà. Thành phố này cũng nổi tiếng với các khu chợ sầm uất như chợ Bến Thành, chợ Tân Định, và các khu phố Tây như Phạm Ngũ Lão, nơi tập trung nhiều du khách quốc tế. TP. HCM cũng là trung tâm của nghệ thuật và giải trí, với các nhà hát, rạp chiếu phim, và các lễ hội văn hóa lớn như Tết Nguyên Đán, lễ hội đường hoa Nguyễn Huệ. Ẩm thực TP. HCM là một điểm nhấn lớn, với sự đa dạng từ các món ăn đường phố như bánh mì, hủ tiếu, đến các món cao cấp như lẩu cua, bò bít tết. TP. HCM cũng là nơi tổ chức nhiều sự kiện quốc tế, như lễ hội pháo hoa, hội chợ du lịch, thu hút hàng triệu du khách mỗi năm."""
                ),
                Destinations(
                    name="Hải Phòng",
                    mood="active",
                    place="city",
                    location="north",
                    description="""Hải Phòng là một thành phố trực thuộc trung ương, nằm ở khu vực Đông Bắc Việt Nam, nổi tiếng với vai trò là thành phố cảng lớn nhất miền Bắc. Hải Phòng có địa hình đa dạng, với cả đồng bằng ven biển và đồi núi, tạo nên một bức tranh thiên nhiên phong phú. Một trong những điểm đến nổi bật của Hải Phòng là đảo Cát Bà, thuộc quần đảo Cát Bà - một di sản thiên nhiên thế giới được UNESCO công nhận, với những bãi biển đẹp, rừng nguyên sinh, và hệ sinh thái đa dạng. Hải Phòng cũng có nhiều di tích lịch sử và văn hóa như đình Hàng Kênh, chùa Dư Hàng, và bãi cọc Bạch Đằng - nơi ghi dấu chiến thắng của quân dân Việt Nam trước quân Nguyên Mông vào thế kỷ 13. Tỉnh này còn nổi tiếng với các lễ hội truyền thống như lễ hội chọi trâu Đồ Sơn, thu hút đông đảo du khách. Ẩm thực Hải Phòng nổi bật với các món như bánh đa cua, bún cá, và nem cua bể. Khí hậu Hải Phòng mang đặc trưng của miền Bắc, với mùa đông lạnh và mùa hè nóng, rất phù hợp để khám phá cả văn hóa và thiên nhiên."""
                ),
                Destinations(
                    name="Đà Nẵng",
                    mood="relaxed",
                    place="beach",
                    location="central",
                    description="""Đà Nẵng là một thành phố trực thuộc trung ương, nằm ở khu vực miền Trung Việt Nam, nổi tiếng với những bãi biển đẹp và sự phát triển hiện đại. Được mệnh danh là "thành phố đáng sống nhất Việt Nam", Đà Nẵng có bãi biển Mỹ Khê - một trong những bãi biển đẹp nhất hành tinh, với bãi cát trắng mịn, nước biển trong xanh, và không khí trong lành. Thành phố này cũng nổi tiếng với các công trình kiến trúc hiện đại như cầu Rồng, cầu Sông Hàn, và Bà Nà Hills - khu du lịch trên núi với cáp treo dài nhất thế giới và Làng Pháp thơ mộng. Về văn hóa, Đà Nẵng có Ngũ Hành Sơn, một quần thể núi đá vôi với các hang động và chùa chiền linh thiêng. Đà Nẵng cũng là cửa ngõ để khám phá các di sản thế giới lân cận như phố cổ Hội An và thánh địa Mỹ Sơn. Khí hậu Đà Nẵng mang đặc trưng của miền Trung, với mùa khô và mùa mưa rõ rệt, rất phù hợp để du lịch biển và khám phá văn hóa. Ẩm thực Đà Nẵng nổi bật với các món như mì Quảng, bánh tráng cuốn thịt heo, và bún chả cá."""
                ),
                Destinations(
                    name="Cần Thơ",
                    mood="chill",
                    place="river",
                    location="south",
                    description="""Cần Thơ là một thành phố trực thuộc trung ương, nằm ở trung tâm vùng đồng bằng sông Cửu Long, được mệnh danh là "Tây Đô" - thủ phủ của miền Tây Nam Bộ. Cần Thơ nổi tiếng với hệ thống sông ngòi, kênh rạch chằng chịt, và những khu chợ nổi trên sông, trong đó chợ nổi Cái Răng là điểm đến không thể bỏ qua. Tại đây, du khách có thể trải nghiệm cảnh mua bán tấp nập trên sông, thưởng thức các món ăn dân dã như bún riêu, bánh cống, và trái cây tươi. Cần Thơ cũng có nhiều điểm đến văn hóa và lịch sử như nhà công tử Bạc Liêu, chùa Ông, và đình Bình Thủy - một công trình kiến trúc cổ kính với phong cách độc đáo. Tỉnh này còn nổi tiếng với các làng nghề truyền thống như làm bánh tráng Thuận Hưng, và các vườn chim tự nhiên như vườn chim Cần Thơ, nơi thu hút nhiều loài chim quý hiếm. Khí hậu Cần Thơ mang đặc trưng nhiệt đới gió mùa, với mùa khô và mùa mưa rõ rệt, tạo điều kiện thuận lợi cho du lịch sinh thái. Ẩm thực Cần Thơ nổi bật với các món như lẩu mắm, cá lóc nướng trui, và bánh tét lá cẩm."""
                ),
                Destinations(
                    name="An Giang",
                    mood="chill",
                    place="river",
                    location="south",
                    description="""An Giang là một tỉnh nằm ở khu vực đồng bằng sông Cửu Long, phía Nam Việt Nam, nổi tiếng với cảnh sắc thiên nhiên hùng vĩ và những giá trị văn hóa đa dạng. Địa hình An Giang đa dạng, với cả đồng bằng và đồi núi, tạo nên một bức tranh thiên nhiên phong phú. Một trong những điểm đến nổi bật của An Giang là rừng tràm Trà Sư, một khu rừng ngập mặn với hệ sinh thái đa dạng, là nơi bảo tồn nhiều loài chim quý hiếm, rất thích hợp để chèo thuyền và khám phá thiên nhiên. An Giang cũng có núi Cấm, một ngọn núi linh thiêng với chùa Vĩnh Nghiêm trên đỉnh, thu hút đông đảo phật tử và du khách. Tỉnh này còn nổi tiếng với các lễ hội truyền thống như lễ hội đua bò Bảy Núi, lễ hội vía Bà Chúa Xứ, thu hút hàng triệu người tham gia. Khí hậu An Giang mang đặc trưng nhiệt đới gió mùa, với mùa khô và mùa mưa rõ rệt, rất phù hợp để khám phá thiên nhiên và văn hóa. Ẩm thực An Giang nổi bật với các món như bún cá Châu Đốc, lẩu mắm, và bánh bò thốt nốt."""
                ),
                Destinations(
                    name="Bà Rịa - Vũng Tàu",
                    mood="relaxed",
                    place="beach",
                    location="south",
                    description="""Bà Rịa - Vũng Tàu là một tỉnh nằm ở khu vực Đông Nam Bộ của Việt Nam, nổi tiếng với những bãi biển đẹp và các khu nghỉ dưỡng cao cấp. Một trong những điểm đến nổi bật của Bà Rịa - Vũng Tàu là bãi biển Vũng Tàu, với bãi cát dài, nước biển trong xanh, và không khí sôi động, thu hút hàng triệu du khách mỗi năm. Tỉnh này cũng có bãi biển Long Hải, với vẻ đẹp hoang sơ, yên bình, rất thích hợp để thư giãn. Bà Rịa - Vũng Tàu còn nổi tiếng với núi Dinh, núi Minh Đạm, nơi có cảnh quan thiên nhiên hùng vĩ và các di tích lịch sử từ thời kháng chiến. Tỉnh này cũng có nhiều di tích văn hóa như đình thần Thắng Tam, nhà lớn Long Sơn, với kiến trúc độc đáo. Khí hậu Bà Rịa - Vũng Tàu mang đặc trưng nhiệt đới gió mùa, với mùa khô và mùa mưa rõ rệt, rất phù hợp để du lịch biển. Ẩm thực Bà Rịa - Vũng Tàu nổi bật với các món như bánh khọt, lẩu súng, và hải sản tươi sống."""
                ),
                Destinations(
                    name="Bắc Giang",
                    mood="chill",
                    place="quiet",
                    location="north",
                    description="""Bắc Giang là một tỉnh nằm ở khu vực Đông Bắc Việt Nam, nổi tiếng với những vườn vải thiều trù phú và các giá trị văn hóa truyền thống. Địa hình Bắc Giang đa dạng, với cả đồng bằng và đồi núi, tạo nên một bức tranh thiên nhiên phong phú. Một trong những điểm đến nổi bật của Bắc Giang là làng vải thiều Lục Ngạn, nơi sản xuất loại vải thiều ngon nhất Việt Nam, thu hút du khách đến tham quan và thưởng thức. Bắc Giang cũng có nhiều di tích lịch sử và văn hóa như chùa Vĩnh Nghiêm, nơi lưu giữ bộ mộc bản kinh Phật quý giá, và khu di tích chiến thắng Xương Giang, nơi ghi dấu chiến thắng của quân Lê trước quân Minh. Tỉnh này còn nổi tiếng với các lễ hội truyền thống như lễ hội chùa Bổ Đà, lễ hội Yên Thế, thu hút đông đảo du khách. Khí hậu Bắc Giang mang đặc trưng của miền Bắc, với bốn mùa rõ rệt, rất phù hợp để khám phá văn hóa và thiên nhiên. Ẩm thực Bắc Giang nổi bật với các món như vải thiều Lục Ngạn, bánh gio, và gà đồi."""
                ),
                Destinations(
                    name="Bắc Kạn",
                    mood="chill",
                    place="mountain",
                    location="north",
                    description="""Bắc Kạn là một tỉnh nằm ở khu vực Đông Bắc Việt Nam, nổi tiếng với cảnh sắc thiên nhiên hùng vĩ và những giá trị văn hóa đa dạng. Địa hình Bắc Kạn chủ yếu là đồi núi, với những dãy núi cao và thung lũng xanh mướt, tạo nên một bức tranh thiên nhiên thơ mộng. Một trong những điểm đến nổi bật của Bắc Kạn là hồ Ba Bể, một trong những hồ nước ngọt lớn nhất Việt Nam, với cảnh quan thơ mộng, những hòn đảo nhỏ, và hệ sinh thái đa dạng, rất thích hợp để chèo thuyền và khám phá thiên nhiên. Bắc Kạn cũng có vườn quốc gia Ba Bể, nơi bảo tồn nhiều loài động thực vật quý hiếm. Tỉnh này còn nổi tiếng với các lễ hội truyền thống như lễ hội Lồng Tồng, lễ hội đình Vĩnh Nghiêm. Khí hậu Bắc Kạn mang đặc trưng của miền Bắc, với mùa đông lạnh và mùa hè mát mẻ, rất phù hợp để khám phá thiên nhiên và văn hóa. Ẩm thực Bắc Kạn nổi bật với các món như cá nướng Ba Bể, tôm chua, và xôi trứng kiến."""
                ),
                Destinations(
                    name="Bạc Liêu",
                    mood="chill",
                    place="quiet",
                    location="south",
                    description="""Bạc Liêu là một tỉnh nằm ở khu vực đồng bằng sông Cửu Long, phía Nam Việt Nam, nổi tiếng với những giá trị văn hóa và lịch sử độc đáo. Địa hình Bạc Liêu chủ yếu là đồng bằng, với đất đai màu mỡ, rất thuận lợi cho nông nghiệp, đặc biệt là trồng lúa và nuôi tôm. Một trong những điểm đến nổi bật của Bạc Liêu là nhà công tử Bạc Liêu, một công trình kiến trúc cổ kính gắn liền với câu chuyện về công tử Bạc Liêu - người nổi tiếng với lối sống xa hoa vào đầu thế kỷ 20. Bạc Liêu cũng có cánh đồng quạt gió, một trong những cánh đồng quạt gió lớn nhất Việt Nam, với cảnh quan độc đáo, rất thích hợp để chụp ảnh. Tỉnh này còn nổi tiếng với các di tích văn hóa như chùa Xiêm Cán, một ngôi chùa Khmer với kiến trúc rực rỡ. Khí hậu Bạc Liêu mang đặc trưng nhiệt đới gió mùa, với mùa khô và mùa mưa rõ rệt, rất phù hợp để khám phá văn hóa và thiên nhiên. Ẩm thực Bạc Liêu nổi bật với các món như bún bò cay, bánh tằm bì, và chả cá Bạc Liêu."""
                ),
                Destinations(
                    name="Bắc Ninh",
                    mood="chill",
                    place="quiet",
                    location="north",
                    description="""Bắc Ninh là một tỉnh nằm ở khu vực Đồng bằng sông Hồng, phía Bắc Việt Nam, nổi tiếng với những giá trị văn hóa và lịch sử lâu đời. Được mệnh danh là "cái nôi của dân ca quan họ", Bắc Ninh là quê hương của các làn điệu quan họ - di sản văn hóa phi vật thể của nhân loại, với những câu hát giao duyên ngọt ngào và sâu lắng. Một trong những điểm đến nổi bật của Bắc Ninh là làng Diềm, nơi tổ chức các lễ hội quan họ truyền thống, thu hút đông đảo du khách. Bắc Ninh cũng có nhiều di tích lịch sử như chùa Phật Tích, chùa Dâu - ngôi chùa cổ nhất Việt Nam, và đền Đô, nơi thờ các vua Lý. Tỉnh này còn nổi tiếng với các làng nghề truyền thống như làng gốm Phù Lãng, làng tranh Đông Hồ, và làng nghề đúc đồng. Khí hậu Bắc Ninh mang đặc trưng của miền Bắc, với bốn mùa rõ rệt, rất phù hợp để khám phá văn hóa và lịch sử. Ẩm thực Bắc Ninh nổi bật với các món như bánh phu thê, nem làng Bùi, và gà Hồ."""
                ),
                Destinations(
                    name="Bến Tre",
                    mood="chill",
                    place="river",
                    location="south",
                    description="""Bến Tre là một tỉnh nằm ở khu vực đồng bằng sông Cửu Long, phía Nam Việt Nam, nổi tiếng với những vườn dừa bạt ngàn và các giá trị văn hóa truyền thống. Được mệnh danh là "xứ dừa", Bến Tre có hàng triệu cây dừa trải dài khắp các huyện, tạo nên một bức tranh thiên nhiên xanh mát. Một trong những điểm đến nổi bật của Bến Tre là cồn Phụng, nơi du khách có thể tham quan các lò làm kẹo dừa, nghe đờn ca tài tử, và thưởng thức các món ăn dân dã. Bến Tre cũng có bãi biển Thừa Đức, với bãi cát dài, nước biển trong xanh, và không khí yên bình, rất thích hợp để thư giãn. Tỉnh này còn nổi tiếng với các di tích lịch sử như khu di tích Đồng Khởi, nơi khởi nguồn phong trào Đồng Khởi năm 1960. Khí hậu Bến Tre mang đặc trưng nhiệt đới gió mùa, với mùa khô và mùa mưa rõ rệt, rất phù hợp để khám phá thiên nhiên và văn hóa. Ẩm thực Bến Tre nổi bật với các món như kẹo dừa, chuột dừa, và bánh xèo ốc gạo."""
                ),
                Destinations(
                    name="Bình Định",
                    mood="relaxed",
                    place="beach",
                    location="central",
                    description="""Bình Định là một tỉnh nằm ở khu vực Nam Trung Bộ của Việt Nam, nổi tiếng với những bãi biển đẹp và bề dày lịch sử văn hóa. Địa hình Bình Định đa dạng, với cả đồng bằng ven biển, đồi núi, và cao nguyên, tạo nên một bức tranh thiên nhiên phong phú. Bãi biển Quy Nhơn là điểm đến nổi bật nhất của Bình Định, với bãi cát vàng óng ánh, nước biển trong xanh, và không khí yên bình, rất thích hợp để thư giãn. Ngoài Quy Nhơn, Bình Định còn có các bãi biển khác như Trung Lương, Nhơn Lý, mang vẻ đẹp hoang sơ hơn. Về lịch sử, Bình Định là quê hương của vua Quang Trung - vị anh hùng dân tộc, và là trung tâm của vương quốc Chăm Pa cổ, với nhiều di tích như tháp Bánh Ít, tháp Dương Long. Tỉnh này cũng nổi tiếng với võ đài Bình Định, nơi sản sinh ra nhiều võ sư nổi tiếng. Ẩm thực Bình Định nổi bật với các món như bánh ít lá gai, tré Bình Định, và hải sản tươi sống. Khí hậu Bình Định mang đặc trưng của miền Trung, với mùa khô và mùa mưa rõ rệt, rất phù hợp để khám phá thiên nhiên và văn hóa."""
                ),
                Destinations(
                    name="Bình Dương",
                    mood="active",
                    place="city",
                    location="south",
                    description="""Bình Dương là một tỉnh nằm ở khu vực Đông Nam Bộ của Việt Nam, nổi tiếng với sự phát triển kinh tế và các giá trị văn hóa truyền thống. Bình Dương là một trong những tỉnh có nền kinh tế phát triển nhất Việt Nam, với nhiều khu công nghiệp lớn và thành phố mới hiện đại như Thủ Dầu Một. Một trong những điểm đến nổi bật của Bình Dương là làng gốm Tân Phước Khánh, nơi sản xuất các sản phẩm gốm sứ nổi tiếng, thu hút du khách đến tham quan và mua sắm. Bình Dương cũng có khu du lịch Đại Nam, với công viên giải trí, đền thờ, và vườn thú, là điểm đến lý tưởng cho gia đình. Tỉnh này còn nổi tiếng với các lễ hội truyền thống như lễ hội chùa Bà Thiên Hậu, thu hút đông đảo du khách và phật tử. Khí hậu Bình Dương mang đặc trưng nhiệt đới gió mùa, với mùa khô và mùa mưa rõ rệt, rất phù hợp để khám phá văn hóa và giải trí. Ẩm thực Bình Dương nổi bật với các món như gà quay xôi phồng, bánh bèo bì, và gỏi gà măng cụt."""
                ),
                Destinations(
                    name="Bình Phước",
                    mood="chill",
                    place="quiet",
                    location="south",
                    description="""Bình Phước là một tỉnh nằm ở khu vực Đông Nam Bộ của Việt Nam, nổi tiếng với những khu rừng nguyên sinh và các giá trị văn hóa đa dạng. Địa hình Bình Phước đa dạng, với cả đồng bằng và đồi núi, tạo nên một bức tranh thiên nhiên phong phú. Một trong những điểm đến nổi bật của Bình Phước là vườn quốc gia Bù Gia Mập, một khu bảo tồn thiên nhiên với hệ sinh thái đa dạng, là nơi bảo tồn nhiều loài động thực vật quý hiếm, rất thích hợp để khám phá thiên nhiên. Bình Phước cũng có hồ Thác Mơ, một hồ nước nhân tạo với cảnh quan thơ mộng, rất thích hợp để chèo thuyền và thư giãn. Tỉnh này còn nổi tiếng với các lễ hội truyền thống như lễ hội cầu mưa của người S’Tiêng, lễ hội mừng lúa mới. Bình Phước cũng là vùng đất của hạt điều, với những đồi điều bạt ngàn. Khí hậu Bình Phước mang đặc trưng nhiệt đới gió mùa, với mùa khô và mùa mưa rõ rệt, rất phù hợp để khám phá thiên nhiên và văn hóa. Ẩm thực Bình Phước nổi bật với các món như ve sầu chiên giòn, gỏi hạt điều, và canh thụt."""
                ),
                Destinations(
                    name="Bình Thuận",
                    mood="relaxed",
                    place="beach",
                    location="central",
                    description="""Bình Thuận là một tỉnh nằm ở khu vực Nam Trung Bộ của Việt Nam, nổi tiếng với những bãi biển đẹp và cảnh sắc thiên nhiên độc đáo. Một trong những điểm đến nổi bật của Bình Thuận là Mũi Né, với những đồi cát bay đỏ rực, bãi biển trong xanh, và các khu nghỉ dưỡng cao cấp, thu hút đông đảo du khách. Bình Thuận cũng có bãi biển Đồi Dương, với bãi cát trắng mịn, nước biển trong xanh, và không khí yên bình. Tỉnh này còn nổi tiếng với ngọn hải đăng Kê Gà, một trong những ngọn hải đăng lâu đời nhất Việt Nam, và đảo Phú Quý, với vẻ đẹp hoang sơ và hệ sinh thái biển đa dạng. Bình Thuận cũng có nhiều di tích lịch sử như tháp Chăm Pô Sah Inư, một công trình kiến trúc Chăm Pa cổ kính. Khí hậu Bình Thuận mang đặc trưng của miền Trung, với mùa khô và mùa mưa rõ rệt, rất phù hợp để du lịch biển. Ẩm thực Bình Thuận nổi bật với các món như bánh canh chả cá, lẩu thả, và nước mắm Phan Thiết."""
                ),
                Destinations(
                    name="Cà Mau",
                    mood="chill",
                    place="river",
                    location="south",
                    description="""Cà Mau là một tỉnh nằm ở cực Nam của Việt Nam, thuộc khu vực đồng bằng sông Cửu Long, nổi tiếng với cảnh sắc thiên nhiên hoang sơ và những giá trị văn hóa truyền thống. Cà Mau là nơi có mũi Cà Mau, điểm cực Nam của tổ quốc, với cột mốc tọa độ quốc gia, thu hút đông đảo du khách đến tham quan và chụp ảnh. Tỉnh này cũng có rừng ngập mặn U Minh Hạ, một khu rừng với hệ sinh thái đa dạng, là nơi bảo tồn nhiều loài động thực vật quý hiếm, rất thích hợp để chèo thuyền và khám phá thiên nhiên. Cà Mau còn nổi tiếng với các làng nghề truyền thống như làm mắm, nuôi ong lấy mật. Khí hậu Cà Mau mang đặc trưng nhiệt đới gió mùa, với mùa khô và mùa mưa rõ rệt, rất phù hợp để khám phá thiên nhiên và văn hóa. Ẩm thực Cà Mau nổi bật với các món như cua rang me, lẩu mắm U Minh, và cá thòi lòi nướng muối ớt."""
                ),
                Destinations(
                    name="Cao Bằng",
                    mood="adventure",
                    place="mountain",
                    location="north",
                    description="""Cao Bằng là một tỉnh nằm ở khu vực Đông Bắc Việt Nam, nổi tiếng với cảnh sắc thiên nhiên hùng vĩ và những giá trị văn hóa đa dạng. Địa hình Cao Bằng chủ yếu là đồi núi, với những dãy núi cao và thung lũng xanh mướt, tạo nên một bức tranh thiên nhiên thơ mộng. Một trong những điểm đến nổi bật của Cao Bằng là thác Bản Giốc, một trong những thác nước đẹp nhất Việt Nam, nằm trên biên giới Việt - Trung, với dòng nước trắng xóa chảy qua những tầng đá vôi, rất thích hợp để chụp ảnh và thư giãn. Cao Bằng cũng có khu di tích Pác Bó, nơi Chủ tịch Hồ Chí Minh từng sống và làm việc trong thời kỳ đầu của cách mạng. Tỉnh này còn nổi tiếng với các lễ hội truyền thống như lễ hội Lồng Tồng, lễ hội đình Phúc Sen. Khí hậu Cao Bằng mang đặc trưng của miền Bắc, với mùa đông lạnh và mùa hè mát mẻ, rất phù hợp để khám phá thiên nhiên và văn hóa. Ẩm thực Cao Bằng nổi bật với các món như vịt quay 7 vị, bánh cuốn trứng, và hạt dẻ Trùng Khánh."""
                ),
                Destinations(
                    name="Đắk Lắk",
                    mood="adventure",
                    place="mountain",
                    location="central",
                    description="""Đắk Lắk là một tỉnh nằm ở khu vực Tây Nguyên của Việt Nam, nổi tiếng với cảnh sắc thiên nhiên hùng vĩ và những giá trị văn hóa đa dạng. Được mệnh danh là "thủ phủ cà phê", Đắk Lắk có những đồi cà phê bạt ngàn, đặc biệt ở khu vực Buôn Ma Thuột, nơi sản xuất loại cà phê ngon nhất Việt Nam. Một trong những điểm đến nổi bật của Đắk Lắk là thác Dray Nur, một ngọn thác hùng vĩ giữa rừng xanh, thu hút du khách yêu thích thiên nhiên. Đắk Lắk cũng có buôn Đôn, nơi du khách có thể trải nghiệm cưỡi voi, khám phá văn hóa của người Ê Đê, và thưởng thức các món ăn truyền thống. Tỉnh này còn nổi tiếng với các lễ hội truyền thống như lễ hội cồng chiêng, lễ hội đua voi. Khí hậu Đắk Lắk mang đặc trưng của Tây Nguyên, với mùa khô và mùa mưa rõ rệt, rất phù hợp để khám phá thiên nhiên và văn hóa. Ẩm thực Đắk Lắk nổi bật với các món như gà nướng, canh lá bép, và cà phê Buôn Ma Thuột."""
                ),
                Destinations(
                    name="Đắk Nông",
                    mood="adventure",
                    place="mountain",
                    location="central",
                    description="""Đắk Nông là một tỉnh nằm ở khu vực Tây Nguyên của Việt Nam, nổi tiếng với cảnh sắc thiên nhiên hùng vĩ và những giá trị văn hóa đa dạng. Địa hình Đắk Nông chủ yếu là đồi núi, với những dãy núi cao và thung lũng xanh mướt, tạo nên một bức tranh thiên nhiên thơ mộng. Một trong những điểm đến nổi bật của Đắk Nông là thác Đắk G’Lun, một ngọn thác hùng vĩ giữa rừng xanh, thu hút du khách yêu thích thiên nhiên. Đắk Nông cũng có vườn quốc gia Tà Đùng, được mệnh danh là "Vịnh Hạ Long của Tây Nguyên", với những hòn đảo nhỏ nổi trên mặt hồ, rất thích hợp để chèo thuyền và khám phá. Tỉnh này còn nổi tiếng với các lễ hội truyền thống như lễ hội cồng chiêng, lễ hội mừng lúa mới. Khí hậu Đắk Nông mang đặc trưng của Tây Nguyên, với mùa khô và mùa mưa rõ rệt, rất phù hợp để khám phá thiên nhiên và văn hóa. Ẩm thực Đắk Nông nổi bật với các món như cá suối nướng, canh lá bép, và rượu cần."""
                ),
                Destinations(
                    name="Điện Biên",
                    mood="adventure",
                    place="mountain",
                    location="north",
                    description="""Điện Biên là một tỉnh nằm ở khu vực Tây Bắc Việt Nam, nổi tiếng với bề dày lịch sử và những giá trị văn hóa đa dạng. Điện Biên là nơi diễn ra chiến thắng Điện Biên Phủ năm 1954, một sự kiện lịch sử quan trọng đánh dấu sự sụp đổ của thực dân Pháp tại Đông Dương. Các di tích lịch sử như đồi A1, hầm De Castries, và bảo tàng Điện Biên Phủ thu hút đông đảo du khách đến tham quan và tìm hiểu. Địa hình Điện Biên chủ yếu là đồi núi, với những dãy núi cao và thung lũng xanh mướt, tạo nên một bức tranh thiên nhiên thơ mộng. Một trong những điểm đến nổi bật của Điện Biên là cánh đồng Mường Thanh, được mệnh danh là "chảo lúa lớn nhất Tây Bắc". Tỉnh này còn nổi tiếng với các lễ hội truyền thống như lễ hội hoa ban, lễ hội đua thuyền. Khí hậu Điện Biên mang đặc trưng của miền Bắc, với mùa đông lạnh và mùa hè mát mẻ, rất phù hợp để khám phá thiên nhiên và lịch sử. Ẩm thực Điện Biên nổi bật với các món như xôi nếp nương, thịt trâu gác bếp, và chẩm chéo."""
                ),
                Destinations(
                    name="Đồng Nai",
                    mood="chill",
                    place="quiet",
                    location="south",
                    description="""Đồng Nai là một tỉnh nằm ở khu vực Đông Nam Bộ của Việt Nam, nổi tiếng với những khu rừng nguyên sinh và các giá trị văn hóa đa dạng. Địa hình Đồng Nai đa dạng, với cả đồng bằng và đồi núi, tạo nên một bức tranh thiên nhiên phong phú. Một trong những điểm đến nổi bật của Đồng Nai là vườn quốc gia Cát Tiên, một khu bảo tồn thiên nhiên với hệ sinh thái đa dạng, nơi bảo tồn nhiều loài động thực vật quý hiếm, rất thích hợp để khám phá thiên nhiên. Đồng Nai cũng có khu du lịch Bửu Long, với cảnh quan núi non, hồ nước, và chùa chiền, mang vẻ đẹp thơ mộng. Tỉnh này còn nổi tiếng với các làng nghề truyền thống như làm gốm Tân Vạn, dệt thổ cẩm. Đồng Nai cũng là một trong những tỉnh có nền kinh tế phát triển, với nhiều khu công nghiệp lớn. Khí hậu Đồng Nai mang đặc trưng nhiệt đới gió mùa, với mùa khô và mùa mưa rõ rệt, rất phù hợp để khám phá thiên nhiên và văn hóa. Ẩm thực Đồng Nai nổi bật với các món như gỏi bưởi, dơi xào lăn, và bánh tráng phơi sương."""
                ),
                Destinations(
                    name="Đồng Tháp",
                    mood="chill",
                    place="river",
                    location="south",
                    description="""Đồng Tháp là một tỉnh nằm ở khu vực đồng bằng sông Cửu Long, phía Nam Việt Nam, nổi tiếng với những cánh đồng sen bạt ngàn và các giá trị văn hóa truyền thống. Địa hình Đồng Tháp chủ yếu là đồng bằng, với đất đai màu mỡ, rất thuận lợi cho nông nghiệp, đặc biệt là trồng lúa và sen. Một trong những điểm đến nổi bật của Đồng Tháp là làng hoa Sa Đéc, nơi sản xuất hàng triệu chậu hoa mỗi năm, đặc biệt rực rỡ vào dịp Tết Nguyên Đán, thu hút đông đảo du khách. Đồng Tháp cũng có khu du lịch Gáo Giồng, một khu rừng tràm với hệ sinh thái đa dạng, là nơi bảo tồn nhiều loài chim quý hiếm, rất thích hợp để chèo thuyền và khám phá thiên nhiên. Tỉnh này còn nổi tiếng với các di tích lịch sử như khu di tích Xẻo Quýt, một căn cứ cách mạng trong kháng chiến chống Mỹ. Khí hậu Đồng Tháp mang đặc trưng nhiệt đới gió mùa, với mùa khô và mùa mưa rõ rệt, rất phù hợp để khám phá thiên nhiên và văn hóa. Ẩm thực Đồng Tháp nổi bật với các món như lẩu cá linh bông điên điển, chuột đồng nướng, và bánh xèo Cao Lãnh."""
                ),
                Destinations(
                    name="Gia Lai",
                    mood="adventure",
                    place="mountain",
                    location="central",
                    description="""Gia Lai là một tỉnh nằm ở khu vực Tây Nguyên của Việt Nam, nổi tiếng với cảnh sắc thiên nhiên hùng vĩ và những giá trị văn hóa đa dạng. Địa hình Gia Lai chủ yếu là đồi núi, với những dãy núi cao và thung lũng xanh mướt, tạo nên một bức tranh thiên nhiên thơ mộng. Một trong những điểm đến nổi bật của Gia Lai là Biển Hồ (hồ T’Nưng), một hồ nước tự nhiên với cảnh quan thơ mộng, được mệnh danh là "đôi mắt Pleiku", rất thích hợp để thư giãn và chụp ảnh. Gia Lai cũng có thác Phú Cường, một ngọn thác hùng vĩ giữa rừng xanh, thu hút du khách yêu thích thiên nhiên. Tỉnh này còn nổi tiếng với các lễ hội truyền thống như lễ hội cồng chiêng, lễ hội đâm trâu. Khí hậu Gia Lai mang đặc trưng của Tây Nguyên, với mùa khô và mùa mưa rõ rệt, rất phù hợp để khám phá thiên nhiên và văn hóa. Ẩm thực Gia Lai nổi bật với các món như phở khô, bò nướng ống tre, và muối kiến vàng."""
                ),
                Destinations(
                    name="Hà Giang",
                    mood="adventure",
                    place="mountain",
                    location="north",
                    description="""Hà Giang là một tỉnh nằm ở cực Bắc của Việt Nam, nổi tiếng với cảnh sắc thiên nhiên hùng vĩ và những giá trị văn hóa đa dạng. Địa hình Hà Giang chủ yếu là đồi núi, với cao nguyên đá Đồng Văn - một di sản địa chất toàn cầu được UNESCO công nhận. Cao nguyên đá Đồng Văn có những dãy núi đá vôi trùng điệp, những thung lũng xanh mướt, và các bản làng của người dân tộc H’Mông, Dao, tạo nên một bức tranh thiên nhiên thơ mộng. Một trong những điểm đến nổi bật của Hà Giang là đèo Mã Pí Lèng, được mệnh danh là "vua của các con đèo" ở Việt Nam, với cảnh quan hùng vĩ và dòng sông Nho Quế uốn lượn bên dưới. Hà Giang cũng nổi tiếng với những ruộng bậc thang Hoàng Su Phì, đặc biệt đẹp vào mùa lúa chín (tháng 9-10). Tỉnh này còn có nhiều lễ hội truyền thống như chợ tình Khâu Vai, lễ hội hoa tam giác mạch, thu hút đông đảo du khách. Ẩm thực Hà Giang nổi bật với các món như thắng cố, thịt trâu gác bếp, và mèn mén. Khí hậu Hà Giang mang đặc trưng của miền Bắc, với mùa đông lạnh và mùa hè mát mẻ, rất phù hợp để khám phá thiên nhiên và văn hóa."""
                ),
                Destinations(
                    name="Hà Nam",
                    mood="chill",
                    place="quiet",
                    location="north",
                    description="""Hà Nam là một tỉnh nằm ở khu vực Đồng bằng sông Hồng, phía Bắc Việt Nam, nổi tiếng với những giá trị văn hóa và tâm linh lâu đời. Địa hình Hà Nam chủ yếu là đồng bằng, với đất đai màu mỡ, rất thuận lợi cho nông nghiệp, đặc biệt là trồng lúa và rau màu. Một trong những điểm đến nổi bật của Hà Nam là chùa Bà Đanh, một ngôi chùa cổ kính nằm bên dòng sông Đáy, mang vẻ đẹp thanh tịnh và huyền bí. Hà Nam cũng có khu du lịch Tam Chúc, với quần thể chùa Tam Chúc - ngôi chùa lớn nhất thế giới, thu hút hàng triệu phật tử và du khách. Tỉnh này còn nổi tiếng với các làng nghề truyền thống như làng trống Đọi Tam, nơi sản xuất những chiếc trống lớn dùng trong các lễ hội. Khí hậu Hà Nam mang đặc trưng của miền Bắc, với bốn mùa rõ rệt, rất phù hợp để khám phá văn hóa và tâm linh. Ẩm thực Hà Nam nổi bật với các món như cá kho làng Vũ Đại, bánh cuốn Phủ Lý, và chè đỗ đen."""
                ),
                Destinations(
                    name="Hà Tĩnh",
                    mood="chill",
                    place="beach",
                    location="central",
                    description="""Hà Tĩnh là một tỉnh nằm ở khu vực Bắc Trung Bộ của Việt Nam, nổi tiếng với bề dày lịch sử và những danh lam thắng cảnh tuyệt đẹp. Địa hình Hà Tĩnh đa dạng, với cả đồng bằng ven biển, đồi núi, và cao nguyên, tạo nên một bức tranh thiên nhiên phong phú. Một trong những điểm đến nổi bật của Hà Tĩnh là bãi biển Thiên Cầm, với bãi cát trắng mịn, nước biển trong xanh, và không khí yên bình, rất thích hợp để thư giãn. Hà Tĩnh cũng có nhiều di tích lịch sử như khu lưu niệm Nguyễn Du - tác giả của Truyện Kiều, và khu di tích Ngã ba Đồng Lộc, nơi ghi dấu sự hy sinh của 10 nữ thanh niên xung phong trong kháng chiến chống Mỹ. Tỉnh này còn nổi tiếng với các làng nghề truyền thống như làm kẹo cu đơ, dệt vải, và nghề rèn. Khí hậu Hà Tĩnh mang đặc trưng của miền Trung, với mùa khô nóng và mùa mưa ẩm, rất phù hợp để khám phá thiên nhiên và lịch sử. Ẩm thực Hà Tĩnh nổi bật với các món như kẹo cu đơ, ram bánh mướt, và hến xúc bánh tráng."""
                ),
                Destinations(
                    name="Hải Dương",
                    mood="chill",
                    place="quiet",
                    location="north",
                    description="""Hải Dương là một tỉnh nằm ở khu vực Đồng bằng sông Hồng, phía Bắc Việt Nam, nổi tiếng với những giá trị văn hóa và lịch sử lâu đời. Địa hình Hải Dương chủ yếu là đồng bằng, với đất đai màu mỡ, rất thuận lợi cho nông nghiệp, đặc biệt là trồng lúa và rau màu. Một trong những điểm đến nổi bật của Hải Dương là Côn Sơn - Kiếp Bạc, một quần thể di tích lịch sử và văn hóa gắn liền với Trần Hưng Đạo và Nguyễn Trãi, thu hút đông đảo du khách và phật tử. Hải Dương cũng có đảo Cò Chi Lăng Nam, một khu vực sinh thái với nhiều loài chim quý hiếm, rất thích hợp để khám phá thiên nhiên. Tỉnh này còn nổi tiếng với các làng nghề truyền thống như làm bánh đậu xanh, gốm Chu Đậu, và chạm khắc gỗ. Khí hậu Hải Dương mang đặc trưng của miền Bắc, với bốn mùa rõ rệt, rất phù hợp để khám phá văn hóa và thiên nhiên. Ẩm thực Hải Dương nổi bật với các món như bánh đậu xanh, bún bò Hải Dương, và rươi Tứ Kỳ."""
                ),
                Destinations(
                    name="Hậu Giang",
                    mood="chill",
                    place="river",
                    location="south",
                    description="""Hậu Giang là một tỉnh nằm ở khu vực đồng bằng sông Cửu Long, phía Nam Việt Nam, nổi tiếng với hệ thống sông ngòi, kênh rạch và những giá trị văn hóa truyền thống. Địa hình Hậu Giang chủ yếu là đồng bằng, với đất đai màu mỡ, rất thuận lợi cho nông nghiệp, đặc biệt là trồng lúa và cây ăn trái. Một trong những điểm đến nổi bật của Hậu Giang là chợ nổi Ngã Bảy (Phụng Hiệp), một khu chợ trên sông tấp nập, thu hút du khách đến khám phá cuộc sống miền Tây. Hậu Giang cũng có khu bảo tồn thiên nhiên Lung Ngọc Hoàng, một vùng đất ngập nước với hệ sinh thái phong phú, là nơi bảo tồn nhiều loài chim quý hiếm. Tỉnh này còn nổi tiếng với các làng nghề truyền thống như làm bánh in, dệt chiếu. Khí hậu Hậu Giang mang đặc trưng nhiệt đới gió mùa, với mùa khô và mùa mưa rõ rệt, rất phù hợp để khám phá thiên nhiên và văn hóa. Ẩm thực Hậu Giang nổi bật với các món như cá lóc nướng trui, lẩu mắm, và bánh cống."""
                ),
                Destinations(
                    name="Hòa Bình",
                    mood="chill",
                    place="mountain",
                    location="north",
                    description="""Hòa Bình là một tỉnh nằm ở khu vực Tây Bắc Việt Nam, nổi tiếng với cảnh sắc thiên nhiên hùng vĩ và những giá trị văn hóa đa dạng. Địa hình Hòa Bình chủ yếu là đồi núi, với những dãy núi cao và thung lũng xanh mướt, tạo nên một bức tranh thiên nhiên thơ mộng. Một trong những điểm đến nổi bật của Hòa Bình là thung lũng Mai Châu, với những cánh đồng lúa xanh mướt, bản làng của người Thái, và không khí yên bình, rất thích hợp để khám phá văn hóa và thiên nhiên. Hòa Bình cũng có hồ Hòa Bình, một hồ nước nhân tạo lớn với cảnh quan thơ mộng, rất thích hợp để chèo thuyền và thư giãn. Tỉnh này còn nổi tiếng với các lễ hội truyền thống như lễ hội Chiềng của người Mường, lễ hội Xên Mường. Khí hậu Hòa Bình mang đặc trưng của miền Bắc, với mùa đông lạnh và mùa hè mát mẻ, rất phù hợp để khám phá thiên nhiên và văn hóa. Ẩm thực Hòa Bình nổi bật với các món như thịt lợn muối chua, cá nướng sông Đà, và cơm lam."""
                ),
                Destinations(
                    name="Hưng Yên",
                    mood="chill",
                    place="quiet",
                    location="north",
                    description="""Hưng Yên là một tỉnh nằm ở khu vực Đồng bằng sông Hồng, phía Bắc Việt Nam, nổi tiếng với những giá trị văn hóa và lịch sử lâu đời. Được mệnh danh là "đất nhãn", Hưng Yên có nhiều vườn nhãn lồng nổi tiếng, đặc biệt là ở khu vực Phố Hiến, nơi từng là một thương cảng sầm uất vào thế kỷ 17. Một trong những điểm đến nổi bật của Hưng Yên là Phố Hiến, với các di tích như chùa Chuông, đền Mẫu, và văn miếu Xích Đằng, nơi lưu giữ nét kiến trúc truyền thống. Hưng Yên cũng có làng nghề truyền thống như làng Nôm, nơi sản xuất đồ gỗ mỹ nghệ, và làng nghề làm tương Bần, một loại tương nổi tiếng dùng trong ẩm thực Việt Nam. Khí hậu Hưng Yên mang đặc trưng của miền Bắc, với bốn mùa rõ rệt, rất phù hợp để khám phá văn hóa và lịch sử. Ẩm thực Hưng Yên nổi bật với các món như nhãn lồng, gà Đông Tảo, và bánh cuốn Phố Hiến."""
                ),
                Destinations(
                    name="Khánh Hòa",
                    mood="relaxed",
                    place="beach",
                    location="central",
                    description="""Khánh Hòa là một tỉnh nằm ở khu vực Nam Trung Bộ của Việt Nam, nổi tiếng với những bãi biển đẹp và các khu nghỉ dưỡng cao cấp. Thành phố Nha Trang, trung tâm của Khánh Hòa, có bãi biển dài hơn 7km, với bãi cát trắng mịn, nước biển trong xanh, và hàng dừa xanh mát, là điểm đến lý tưởng để thư giãn và tắm biển. Nha Trang còn có nhiều hòn đảo đẹp như Hòn Mun, Hòn Tằm, và Hòn Chồng, nơi du khách có thể lặn ngắm san hô, tham gia các hoạt động thể thao dưới nước, hoặc khám phá cuộc sống của ngư dân. Một trong những điểm đến nổi bật của Khánh Hòa là khu du lịch Vinpearl, với công viên giải trí, thủy cung, và các khách sạn sang trọng. Về văn hóa, Khánh Hòa có tháp Bà Ponagar - một công trình kiến trúc Chăm Pa cổ kính, và viện Hải dương học, nơi trưng bày nhiều loài sinh vật biển quý hiếm. Ẩm thực Khánh Hòa nổi bật với các món như bún sứa, hải sản tươi sống, và nem nướng Ninh Hòa. Khí hậu Khánh Hòa mang đặc trưng của miền Trung, với mùa khô và mùa mưa rõ rệt, rất phù hợp để du lịch biển."""
                ),
                Destinations(
                    name="Kiên Giang",
                    mood="chill",
                    place="quiet",
                    location="beach",
                    description="""Kiên Giang là một tỉnh thuộc vùng đồng bằng sông Cửu Long, nằm ở phía Tây Nam của Việt Nam, nổi tiếng với vẻ đẹp của các hòn đảo và bãi biển. Điểm nhấn lớn nhất của Kiên Giang là đảo Phú Quốc, được mệnh danh là "đảo ngọc" với những bãi biển cát trắng mịn như Bãi Sao, Bãi Dài, và nước biển trong xanh. Phú Quốc không chỉ là nơi lý tưởng để nghỉ dưỡng mà còn nổi tiếng với các hoạt động như lặn ngắm san hô, khám phá làng chài, và thưởng thức nước mắm - đặc sản trứ danh của vùng. Ngoài Phú Quốc, Kiên Giang còn có quần đảo Nam Du với hơn 20 hòn đảo lớn nhỏ, mang vẻ đẹp hoang sơ, yên bình, rất thích hợp cho những ai yêu thích sự tĩnh lặng. Tỉnh này cũng có nhiều di tích lịch sử và văn hóa như chùa Hang, đình thần Nguyễn Trung Trực, người anh hùng dân tộc chống Pháp. Khí hậu Kiên Giang mang đặc trưng nhiệt đới gió mùa, với mùa khô và mùa mưa rõ rệt, tạo điều kiện thuận lợi cho du lịch quanh năm. Ẩm thực Kiên Giang nổi bật với các món như bún cá Kiên Giang, gỏi cá trích, và bánh thốt nốt."""
                ),
                Destinations(
                    name="Kon Tum",
                    mood="adventure",
                    place="mountain",
                    location="central",
                    description="""Kon Tum là một tỉnh nằm ở khu vực Tây Nguyên của Việt Nam, nổi tiếng với cảnh sắc thiên nhiên hùng vĩ và những giá trị văn hóa đa dạng. Địa hình Kon Tum chủ yếu là đồi núi, với những dãy núi cao và thung lũng xanh mướt, tạo nên một bức tranh thiên nhiên thơ mộng. Một trong những điểm đến nổi bật của Kon Tum là nhà rông Kon Klor, một công trình kiến trúc truyền thống của người Ba Na, với mái nhà cao vút, là biểu tượng văn hóa của Tây Nguyên. Kon Tum cũng có khu du lịch Măng Đen, được mệnh danh là "Đà Lạt thứ hai", với khí hậu mát mẻ, rừng thông bạt ngàn, và không khí yên bình, rất thích hợp để nghỉ dưỡng. Tỉnh này còn nổi tiếng với các lễ hội truyền thống như lễ hội cồng chiêng, lễ hội đâm trâu. Khí hậu Kon Tum mang đặc trưng của Tây Nguyên, với mùa khô và mùa mưa rõ rệt, rất phù hợp để khám phá thiên nhiên và văn hóa. Ẩm thực Kon Tum nổi bật với các món như gỏi lá, cá suối nướng, và cơm lam."""
                ),
                Destinations(
                    name="Lai Châu",
                    mood="adventure",
                    place="mountain",
                    location="north",
                    description="""Lai Châu là một tỉnh nằm ở khu vực Tây Bắc Việt Nam, nổi tiếng với cảnh sắc thiên nhiên hùng vĩ và những giá trị văn hóa đa dạng. Địa hình Lai Châu chủ yếu là đồi núi, với những dãy núi cao và thung lũng xanh mướt, tạo nên một bức tranh thiên nhiên thơ mộng. Một trong những điểm đến nổi bật của Lai Châu là đỉnh Pu Si Lung, một trong những đỉnh núi cao nhất Việt Nam, là điểm đến lý tưởng cho những ai yêu thích leo núi. Lai Châu cũng có nhiều suối nước nóng tự nhiên như suối nước nóng Vàng Bó, rất thích hợp để nghỉ dưỡng và thư giãn. Tỉnh này còn nổi tiếng với các lễ hội truyền thống như lễ hội Then Kin Pang của người Thái, lễ hội Gầu Tào của người H’Mông. Khí hậu Lai Châu mang đặc trưng của miền Bắc, với mùa đông lạnh và mùa hè mát mẻ, rất phù hợp để khám phá thiên nhiên và văn hóa. Ẩm thực Lai Châu nổi bật với các món như xôi tím, cá nướng Pa Pỉnh Tộp, và măng đắng."""
                ),
                Destinations(
                    name="Lâm Đồng",
                    mood="relaxed",
                    place="mountain",
                    location="central",
                    description="""Lâm Đồng là một tỉnh nằm ở khu vực Tây Nguyên của Việt Nam, nổi tiếng với cảnh sắc thiên nhiên hùng vĩ và khí hậu mát mẻ quanh năm. Một trong những điểm đến nổi bật của Lâm Đồng là thành phố Đà Lạt, được mệnh danh là "thành phố ngàn hoa", với những đồi thông bạt ngàn, hồ Xuân Hương thơ mộng, và các loài hoa rực rỡ như cẩm tú cầu, hoa mai anh đào. Đà Lạt cũng có nhiều điểm tham quan như thung lũng Tình Yêu, thác Datanla, và làng Cù Lần, rất thích hợp để nghỉ dưỡng và khám phá thiên nhiên. Lâm Đồng còn nổi tiếng với các đồi chè Cầu Đất, nơi sản xuất loại chè xanh thơm ngon, và các vườn dâu tây trù phú. Tỉnh này cũng có nhiều di tích văn hóa như nhà thờ Con Gà, ga Đà Lạt, với kiến trúc độc đáo. Khí hậu Lâm Đồng mang đặc trưng của Tây Nguyên, với mùa khô và mùa mưa rõ rệt, rất phù hợp để du lịch nghỉ dưỡng. Ẩm thực Lâm Đồng nổi bật với các món như bánh tráng nướng, lẩu gà lá é, và mứt Đà Lạt."""
                ),
                Destinations(
                    name="Lạng Sơn",
                    mood="chill",
                    place="quiet",
                    location="mountain",
                    description="""Lạng Sơn là một tỉnh miền núi nằm ở phía Đông Bắc Việt Nam, giáp với Trung Quốc, nổi tiếng với cảnh sắc thiên nhiên hùng vĩ và những di tích lịch sử lâu đời. Địa hình Lạng Sơn chủ yếu là đồi núi, với những dãy núi đá vôi trùng điệp và thung lũng xanh mướt, tạo nên một bức tranh thiên nhiên thơ mộng. Một trong những điểm đến nổi bật của Lạng Sơn là động Tam Thanh, một hang động tự nhiên với những nhũ đá lấp lánh và không gian huyền bí, bên trong còn có chùa Tam Thanh - nơi linh thiêng thu hút nhiều du khách. Lạng Sơn cũng là vùng đất giàu giá trị lịch sử, với các di tích như Ải Chi Lăng - nơi ghi dấu chiến thắng của quân dân Việt Nam trước quân Minh vào thế kỷ 15. Ngoài ra, Lạng Sơn còn nổi tiếng với các phiên chợ biên giới như chợ Đông Kinh, nơi giao thoa văn hóa Việt - Trung, và các sản phẩm đặc sản như vịt quay lá mắc mật, rượu Mẫu Sơn, và đào Lạng Sơn. Khí hậu Lạng Sơn mang đặc trưng của miền Bắc, với mùa đông lạnh và mùa hè mát mẻ, rất phù hợp để khám phá thiên nhiên và văn hóa."""
                ),
                Destinations(
                    name="Lào Cai",
                    mood="adventure",
                    place="mountain",
                    location="north",
                    description="""Lào Cai là một tỉnh nằm ở khu vực Tây Bắc Việt Nam, nổi tiếng với cảnh sắc thiên nhiên hùng vĩ và những giá trị văn hóa đa dạng. Địa hình Lào Cai chủ yếu là đồi núi, với những dãy núi cao và thung lũng xanh mướt, tạo nên một bức tranh thiên nhiên thơ mộng. Một trong những điểm đến nổi bật của Lào Cai là Sa Pa, một thị trấn trên núi với khí hậu mát mẻ quanh năm, những ruộng bậc thang tuyệt đẹp, và các bản làng của người dân tộc H’Mông, Dao, thu hút đông đảo du khách. Lào Cai cũng có đỉnh Fansipan, được mệnh danh là "nóc nhà Đông Dương", là điểm đến lý tưởng cho những ai yêu thích leo núi. Tỉnh này còn nổi tiếng với các phiên chợ vùng cao như chợ Bắc Hà, nơi giao thoa văn hóa của các dân tộc thiểu số. Khí hậu Lào Cai mang đặc trưng của miền Bắc, với mùa đông lạnh và mùa hè mát mẻ, rất phù hợp để khám phá thiên nhiên và văn hóa. Ẩm thực Lào Cai nổi bật với các món như thắng cố, lợn cắp nách, và măng đắng."""
                ),
                Destinations(
                    name="Long An",
                    mood="chill",
                    place="river",
                    location="south",
                    description="""Long An là một tỉnh nằm ở khu vực đồng bằng sông Cửu Long, phía Nam Việt Nam, nổi tiếng với hệ thống sông ngòi, kênh rạch và những giá trị văn hóa truyền thống. Địa hình Long An chủ yếu là đồng bằng, với đất đai màu mỡ, rất thuận lợi cho nông nghiệp, đặc biệt là trồng lúa và thanh long. Một trong những điểm đến nổi bật của Long An là làng nổi Tân Lập, một khu rừng tràm xanh mướt với hệ sinh thái đa dạng, rất thích hợp để chèo thuyền và khám phá thiên nhiên. Long An cũng có khu di tích lịch sử Láng Sen, một vùng đất ngập nước với hệ sinh thái phong phú, là nơi bảo tồn nhiều loài chim quý hiếm. Tỉnh này còn nổi tiếng với các lễ hội truyền thống như lễ hội Làm Chay, lễ hội đình Vĩnh Nghiêm. Khí hậu Long An mang đặc trưng nhiệt đới gió mùa, với mùa khô và mùa mưa rõ rệt, rất phù hợp để khám phá thiên nhiên và văn hóa. Ẩm thực Long An nổi bật với các món như lẩu mắm, canh chua cá lóc, và thanh long Châu Thành."""
                ),
                Destinations(
                    name="Nam Định",
                    mood="chill",
                    place="quiet",
                    location="north",
                    description="""Nam Định là một tỉnh nằm ở khu vực Đồng bằng sông Hồng, phía Bắc Việt Nam, nổi tiếng với bề dày lịch sử và những giá trị văn hóa truyền thống. Nam Định là quê hương của triều đại nhà Trần, với nhiều di tích lịch sử như chùa Phổ Minh, nơi lưu giữ tháp Phổ Minh - một công trình kiến trúc cổ kính. Tỉnh này cũng có khu bảo tồn thiên nhiên đất ngập nước Vườn quốc gia Xuân Thủy, nơi thu hút nhiều loài chim di cư quý hiếm. Về văn hóa, Nam Định nổi tiếng với các lễ hội truyền thống như lễ hội chùa Keo, lễ hội Phủ Dầy, và các làng nghề như làng tranh Đông Hồ, làng nghề đúc đồng. Nam Định cũng có bãi biển Thịnh Long, với bãi cát dài và không khí yên bình, rất thích hợp để thư giãn. Khí hậu Nam Định mang đặc trưng của miền Bắc, với bốn mùa rõ rệt, rất phù hợp để khám phá văn hóa và thiên nhiên. Ẩm thực Nam Định nổi bật với các món như phở bò Nam Định, bánh gai, và kẹo Sìu Châu."""
                ),
                Destinations(
                    name="Nghệ An",
                    mood="active",
                    place="city",
                    location="central",
                    description="""Nghệ An là một tỉnh nằm ở khu vực Bắc Trung Bộ của Việt Nam, nổi tiếng với bề dày lịch sử và những danh lam thắng cảnh tuyệt đẹp. Nghệ An là quê hương của Chủ tịch Hồ Chí Minh, với làng Sen (Kim Liên) - nơi Bác sinh ra và lớn lên, thu hút hàng triệu du khách đến tham quan và tưởng niệm. Tỉnh này có bãi biển Cửa Lò, một trong những bãi biển đẹp nhất miền Trung, với bãi cát trắng mịn, nước biển trong xanh, và không khí sôi động. Nghệ An cũng có nhiều điểm đến thiên nhiên như vườn quốc gia Pù Mát, nơi bảo tồn nhiều loài động thực vật quý hiếm, và cánh đồng hoa hướng dương ở Nghĩa Đàn, thu hút đông đảo du khách chụp ảnh. Về văn hóa, Nghệ An nổi tiếng với các làn điệu dân ca ví, giặm - di sản văn hóa phi vật thể của nhân loại. Khí hậu Nghệ An mang đặc trưng của miền Trung, với mùa khô nóng và mùa mưa ẩm, rất phù hợp để khám phá thiên nhiên và lịch sử. Ẩm thực Nghệ An nổi bật với các món như cháo lươn, bánh mướt, và súp lươn."""
                ),
                Destinations(
                    name="Ninh Bình",
                    mood="chill",
                    place="quiet",
                    location="north",
                    description="""Ninh Bình là một tỉnh nằm ở khu vực Đồng bằng sông Hồng, phía Bắc Việt Nam, nổi tiếng với cảnh sắc thiên nhiên hùng vĩ và những giá trị văn hóa lâu đời. Được mệnh danh là "Vịnh Hạ Long trên cạn", Ninh Bình có khu du lịch Tràng An - một di sản văn hóa và thiên nhiên thế giới được UNESCO công nhận, với những dãy núi đá vôi, hang động, và dòng sông uốn lượn, rất thích hợp để chèo thuyền ngắm cảnh. Ninh Bình cũng có cố đô Hoa Lư, kinh đô của Việt Nam vào thế kỷ 10 dưới thời nhà Đinh và nhà Tiền Lê, với các đền thờ vua Đinh Tiên Hoàng và vua Lê Đại Hành. Tỉnh này còn nổi tiếng với chùa Bái Đính, một trong những ngôi chùa lớn nhất Đông Nam Á, thu hút hàng triệu phật tử và du khách. Khí hậu Ninh Bình mang đặc trưng của miền Bắc, với bốn mùa rõ rệt, rất phù hợp để khám phá thiên nhiên và văn hóa. Ẩm thực Ninh Bình nổi bật với các món như thịt dê, cơm cháy, và gỏi cá nhệch."""
                ),
                Destinations(
                    name="Ninh Thuận",
                    mood="relaxed",
                    place="beach",
                    location="central",
                    description="""Ninh Thuận là một tỉnh nằm ở khu vực Nam Trung Bộ của Việt Nam, nổi tiếng với những bãi biển đẹp và các giá trị văn hóa đa dạng. Một trong những điểm đến nổi bật của Ninh Thuận là bãi biển Ninh Chữ, với bãi cát trắng mịn, nước biển trong xanh, và không khí yên bình, rất thích hợp để thư giãn. Ninh Thuận cũng có vịnh Vĩnh Hy, một trong những vịnh biển đẹp nhất Việt Nam, với làn nước trong xanh và hệ sinh thái biển đa dạng, rất thích hợp để lặn ngắm san hô. Tỉnh này còn nổi tiếng với các di tích văn hóa như tháp Chăm Pô Klong Garai, một công trình kiến trúc Chăm Pa cổ kính, và làng gốm Bàu Trúc, nơi sản xuất các sản phẩm gốm truyền thống. Ninh Thuận cũng là vùng đất của nho và táo, với những vườn nho trù phú ở Phan Rang. Khí hậu Ninh Thuận mang đặc trưng của miền Trung, với mùa khô và mùa mưa rõ rệt, rất phù hợp để du lịch biển. Ẩm thực Ninh Thuận nổi bật với các món như thịt dê nướng, gỏi cá mai, và bánh canh chả cá."""
                ),
                Destinations(
                    name="Phú Thọ",
                    mood="chill",
                    place="quiet",
                    location="north",
                    description="""Phú Thọ là một tỉnh nằm ở khu vực Đông Bắc Việt Nam, nổi tiếng với bề dày lịch sử và những giá trị văn hóa truyền thống. Được mệnh danh là "đất tổ vua Hùng", Phú Thọ là nơi đặt đền Hùng - nơi thờ cúng các vua Hùng, tổ tiên của dân tộc Việt Nam, thu hút hàng triệu người dân về giỗ tổ vào ngày 10/3 âm lịch. Địa hình Phú Thọ đa dạng, với cả đồng bằng và đồi núi, tạo nên một bức tranh thiên nhiên phong phú. Một trong những điểm đến nổi bật của Phú Thọ là vườn quốc gia Xuân Sơn, với hệ sinh thái đa dạng, những cánh rừng nguyên sinh, và các suối nước nóng tự nhiên, rất thích hợp để khám phá thiên nhiên. Phú Thọ cũng nổi tiếng với các làn điệu hát Xoan - di sản văn hóa phi vật thể của nhân loại. Khí hậu Phú Thọ mang đặc trưng của miền Bắc, với bốn mùa rõ rệt, rất phù hợp để khám phá văn hóa và lịch sử. Ẩm thực Phú Thọ nổi bật với các món như bánh chưng, bánh giầy, thịt chua, và cá sông."""
                ),
                Destinations(
                    name="Phú Yên",
                    mood="relaxed",
                    place="beach",
                    location="central",
                    description="""Phú Yên là một tỉnh nằm ở khu vực Nam Trung Bộ của Việt Nam, nổi tiếng với những bãi biển hoang sơ và cảnh sắc thiên nhiên tuyệt đẹp. Địa hình Phú Yên đa dạng, với cả đồng bằng ven biển, đồi núi, và cao nguyên, tạo nên một bức tranh thiên nhiên phong phú. Một trong những điểm đến nổi bật của Phú Yên là Ghềnh Đá Đĩa, một kỳ quan thiên nhiên với những cột đá bazan hình lục giác xếp chồng lên nhau, được hình thành từ hoạt động núi lửa hàng triệu năm trước, rất thích hợp để chụp ảnh và khám phá. Phú Yên cũng có bãi biển Long Thủy, với bãi cát trắng mịn, nước biển trong xanh, và không khí yên bình. Tỉnh này còn nổi tiếng với đầm Ô Loan, một vùng đầm nước lợ với cảnh quan thơ mộng, và tháp Nhạn, một công trình kiến trúc Chăm Pa cổ kính. Khí hậu Phú Yên mang đặc trưng của miền Trung, với mùa khô và mùa mưa rõ rệt, rất phù hợp để du lịch biển. Ẩm thực Phú Yên nổi bật với các món như mắt cá ngừ đại dương, sò huyết đầm Ô Loan, và bánh ướt chả bò."""
                ),
                Destinations(
                    name="Quảng Bình",
                    mood="adventure",
                    place="mountain",
                    location="central",
                    description="""Quảng Bình là một tỉnh nằm ở khu vực Bắc Trung Bộ của Việt Nam, nổi tiếng với những hang động kỳ vĩ và cảnh sắc thiên nhiên tuyệt đẹp. Điểm nhấn lớn nhất của Quảng Bình là Vườn quốc gia Phong Nha - Kẻ Bàng, một di sản thiên nhiên thế giới được UNESCO công nhận, với hệ thống hang động đồ sộ như động Phong Nha, động Thiên Đường, và hang Sơn Đoòng - hang động lớn nhất thế giới. Du khách có thể chèo thuyền trên sông Son để khám phá động Phong Nha, với những nhũ đá lấp lánh và không gian huyền bí. Quảng Bình cũng có bãi biển Nhật Lệ, với bãi cát trắng mịn, nước biển trong xanh, và không khí yên bình, rất thích hợp để thư giãn. Tỉnh này còn nổi tiếng với các di tích lịch sử như đồi cát Quang Phú, nơi mang vẻ đẹp hoang sơ, và các làng nghề truyền thống như làm nón, dệt vải. Khí hậu Quảng Bình mang đặc trưng của miền Trung, với mùa khô và mùa mưa rõ rệt, rất phù hợp để khám phá thiên nhiên và văn hóa. Ẩm thực Quảng Bình nổi bật với các món như bánh bột lọc, cháo canh, và lẩu cá khoai."""
                ),
                Destinations(
                    name="Quảng Nam",
                    mood="chill",
                    place="quiet",
                    location="central",
                    description="""Quảng Nam là một tỉnh nằm ở khu vực miền Trung Việt Nam, nổi tiếng với những di sản văn hóa thế giới và cảnh sắc thiên nhiên tuyệt đẹp. Một trong những điểm đến nổi bật của Quảng Nam là phố cổ Hội An, một di sản văn hóa thế giới được UNESCO công nhận, với những con phố cổ kính, đèn lồng rực rỡ, và không khí yên bình, thu hút hàng triệu du khách. Quảng Nam cũng có thánh địa Mỹ Sơn, một quần thể đền tháp Chăm Pa cổ kính, là trung tâm tôn giáo của vương quốc Chăm Pa xưa. Tỉnh này còn có bãi biển Cửa Đại, với bãi cát trắng mịn, nước biển trong xanh, rất thích hợp để thư giãn. Quảng Nam cũng nổi tiếng với các làng nghề truyền thống như làng gốm Thanh Hà, làng mộc Kim Bồng. Khí hậu Quảng Nam mang đặc trưng của miền Trung, với mùa khô và mùa mưa rõ rệt, rất phù hợp để khám phá văn hóa và thiên nhiên. Ẩm thực Quảng Nam nổi bật với các món như cao lầu, mì Quảng, và bánh bèo."""
                ),
                Destinations(
                    name="Quảng Ngãi",
                    mood="chill",
                    place="beach",
                    location="central",
                    description="""Quảng Ngãi là một tỉnh nằm ở khu vực miền Trung Việt Nam, nổi tiếng với những bãi biển đẹp và bề dày lịch sử. Một trong những điểm đến nổi bật của Quảng Ngãi là đảo Lý Sơn, được mệnh danh là "vương quốc tỏi", với những bãi biển trong xanh, cánh đồng tỏi bạt ngàn, và cảnh quan núi lửa độc đáo, rất thích hợp để khám phá thiên nhiên. Quảng Ngãi cũng có bãi biển Mỹ Khê, với bãi cát trắng mịn, nước biển trong xanh, và không khí yên bình. Về lịch sử, Quảng Ngãi là nơi diễn ra vụ thảm sát Mỹ Lai năm 1968, với khu chứng tích Sơn Mỹ, thu hút du khách đến tìm hiểu về chiến tranh Việt Nam. Tỉnh này còn nổi tiếng với các làng nghề truyền thống như làm đường phổi, dệt thổ cẩm. Khí hậu Quảng Ngãi mang đặc trưng của miền Trung, với mùa khô và mùa mưa rõ rệt, rất phù hợp để khám phá thiên nhiên và lịch sử. Ẩm thực Quảng Ngãi nổi bật với các món như cá bống sông Trà, don, và ram bắp."""
                ),
                Destinations(
                    name="Quảng Ninh",
                    mood="adventure",
                    place="beach",
                    location="north",
                    description="""Quảng Ninh là một tỉnh nằm ở khu vực Đông Bắc Việt Nam, nổi tiếng với Vịnh Hạ Long - một di sản thiên nhiên thế giới được UNESCO công nhận. Vịnh Hạ Long có hàng nghìn hòn đảo đá vôi lớn nhỏ, với những hang động kỳ vĩ như hang Sửng Sốt, hang Đầu Gỗ, và đảo Titop, nơi du khách có thể chèo thuyền kayak, ngắm cảnh, hoặc leo núi để chiêm ngưỡng toàn cảnh vịnh. Quảng Ninh cũng có đảo Cô Tô, với những bãi biển hoang sơ, nước biển trong xanh, và không khí yên bình, rất thích hợp để thư giãn. Tỉnh này còn nổi tiếng với các di tích lịch sử và văn hóa như chùa Yên Tử - cái nôi của thiền phái Trúc Lâm, và khu di tích Bạch Đằng, nơi ghi dấu chiến thắng của quân dân Việt Nam trước quân Nguyên Mông. Khí hậu Quảng Ninh mang đặc trưng của miền Bắc, với bốn mùa rõ rệt, rất phù hợp để khám phá cả thiên nhiên và văn hóa. Ẩm thực Quảng Ninh nổi bật với các món như chả mực, bánh cuốn chả mực, và hải sản tươi sống."""
                ),
                Destinations(
                    name="Quảng Trị",
                    mood="chill",
                    place="quiet",
                    location="central",
                    description="""Quảng Trị là một tỉnh nằm ở khu vực Bắc Trung Bộ của Việt Nam, nổi tiếng với bề dày lịch sử và những giá trị văn hóa truyền thống. Quảng Trị là vùng đất gắn liền với cuộc kháng chiến chống Mỹ, với các di tích lịch sử như Thành cổ Quảng Trị, cầu Hiền Lương, và địa đạo Vịnh Mốc, thu hút du khách đến tìm hiểu về chiến tranh Việt Nam. Tỉnh này cũng có bãi biển Cửa Tùng, với bãi cát trắng mịn, nước biển trong xanh, và không khí yên bình, rất thích hợp để thư giãn. Quảng Trị còn nổi tiếng với các làng nghề truyền thống như làm nón, dệt thổ cẩm. Khí hậu Quảng Trị mang đặc trưng của miền Trung, với mùa khô và mùa mưa rõ rệt, rất phù hợp để khám phá lịch sử và thiên nhiên. Ẩm thực Quảng Trị nổi bật với các món như cháo vạt giường, bánh ướt thịt nướng, và bún hến."""
                ),
                Destinations(
                    name="Sóc Trăng",
                    mood="chill",
                    place="river",
                    location="south",
                    description="""Sóc Trăng là một tỉnh nằm ở khu vực đồng bằng sông Cửu Long, phía Nam Việt Nam, nổi tiếng với những giá trị văn hóa đa dạng và cảnh sắc thiên nhiên yên bình. Địa hình Sóc Trăng chủ yếu là đồng bằng, với đất đai màu mỡ, rất thuận lợi cho nông nghiệp, đặc biệt là trồng lúa và cây ăn trái. Một trong những điểm đến nổi bật của Sóc Trăng là chùa Mahatup (chùa Dơi), một ngôi chùa của người Khmer với kiến trúc độc đáo, là nơi trú ngụ của hàng ngàn con dơi, thu hút đông đảo du khách. Sóc Trăng cũng có vườn cò Tân Long, một khu vực sinh thái với không gian yên bình, là nơi bảo tồn nhiều loài chim quý hiếm. Tỉnh này còn nổi tiếng với các lễ hội truyền thống như lễ hội Ok Om Bok, lễ hội đua ghe ngo, thu hút hàng triệu người tham gia. Khí hậu Sóc Trăng mang đặc trưng nhiệt đới gió mùa, với mùa khô và mùa mưa rõ rệt, rất phù hợp để khám phá văn hóa và thiên nhiên. Ẩm thực Sóc Trăng nổi bật với các món như bún gỏi dà, bánh pía, và cháo cá lóc."""
                ),
                Destinations(
                    name="Sơn La",
                    mood="adventure",
                    place="mountain",
                    location="north",
                    description="""Sơn La là một tỉnh nằm ở khu vực Tây Bắc Việt Nam, nổi tiếng với cảnh sắc thiên nhiên hùng vĩ và những giá trị văn hóa đa dạng. Địa hình Sơn La chủ yếu là đồi núi, với những dãy núi cao và thung lũng xanh mướt, tạo nên một bức tranh thiên nhiên thơ mộng. Một trong những điểm đến nổi bật của Sơn La là cao nguyên Mộc Châu, với những đồi chè xanh mướt, cánh đồng hoa cải, và khí hậu mát mẻ quanh năm, rất thích hợp để nghỉ dưỡng và khám phá thiên nhiên. Sơn La cũng có nhà tù Sơn La, một di tích lịch sử ghi dấu thời kỳ kháng chiến chống Pháp. Tỉnh này còn nổi tiếng với các lễ hội truyền thống như lễ hội Xên Mường của người Thái, lễ hội hoa ban. Khí hậu Sơn La mang đặc trưng của miền Bắc, với mùa đông lạnh và mùa hè mát mẻ, rất phù hợp để khám phá thiên nhiên và văn hóa. Ẩm thực Sơn La nổi bật với các món như bê chao, nậm pịa, và cơm lam."""
                ),
                Destinations(
                    name="Tây Ninh",
                    mood="chill",
                    place="quiet",
                    location="south",
                    description="""Tây Ninh là một tỉnh nằm ở khu vực Đông Nam Bộ của Việt Nam, nổi tiếng với những giá trị văn hóa và tâm linh lâu đời. Một trong những điểm đến nổi bật của Tây Ninh là núi Bà Đen, một ngọn núi linh thiêng với chùa Bà Đen trên đỉnh, thu hút hàng triệu phật tử và du khách đến hành hương. Tây Ninh cũng là trung tâm của đạo Cao Đài, với Tòa Thánh Tây Ninh - một công trình kiến trúc độc đáo, là nơi diễn ra các nghi lễ tôn giáo đặc sắc. Tỉnh này còn có hồ Dầu Tiếng, một hồ nước nhân tạo lớn với cảnh quan thơ mộng, rất thích hợp để chèo thuyền và thư giãn. Tây Ninh cũng nổi tiếng với các làng nghề truyền thống như làm bánh tráng phơi sương, dệt chiếu. Khí hậu Tây Ninh mang đặc trưng nhiệt đới gió mùa, với mùa khô và mùa mưa rõ rệt, rất phù hợp để khám phá văn hóa và tâm linh. Ẩm thực Tây Ninh nổi bật với các món như bánh tráng phơi sương, bò tùng xẻo, và muối ớt chanh."""
                ),
                Destinations(
                    name="Thái Bình",
                    mood="chill",
                    place="quiet",
                    location="north",
                    description="""Thái Bình là một tỉnh nằm ở khu vực Đồng bằng sông Hồng, phía Bắc Việt Nam, nổi tiếng với những cánh đồng lúa bát ngát và các giá trị văn hóa truyền thống. Được mệnh danh là "quê lúa", Thái Bình có địa hình chủ yếu là đồng bằng, với đất đai màu mỡ, rất thuận lợi cho nông nghiệp, đặc biệt là trồng lúa. Một trong những điểm đến nổi bật của Thái Bình là bãi biển Đồng Châu, với bãi cát dài, rừng phi lao xanh mát, và không khí yên bình, rất thích hợp để thư giãn. Thái Bình cũng có nhiều di tích lịch sử và văn hóa như chùa Keo, một ngôi chùa cổ kính với kiến trúc độc đáo, và đền Trần, nơi thờ các vua Trần. Tỉnh này còn nổi tiếng với các lễ hội truyền thống như lễ hội chùa Keo, lễ hội đền Trần, thu hút đông đảo du khách. Khí hậu Thái Bình mang đặc trưng của miền Bắc, với bốn mùa rõ rệt, rất phù hợp để khám phá văn hóa và thiên nhiên. Ẩm thực Thái Bình nổi bật với các món như bánh cáy, canh cá Quỳnh Côi, và bún bung hoa chuối."""
                ),
                Destinations(
                    name="Thái Nguyên",
                    mood="chill",
                    place="mountain",
                    location="north",
                    description="""Thái Nguyên là một tỉnh nằm ở khu vực Đông Bắc Việt Nam, nổi tiếng với những đồi chè xanh mướt và các giá trị văn hóa truyền thống. Được mệnh danh là "thủ phủ chè Việt Nam", Thái Nguyên có những đồi chè Tân Cương nổi tiếng, nơi sản xuất loại chè xanh thơm ngon nhất Việt Nam, thu hút du khách đến tham quan và thưởng thức. Một trong những điểm đến nổi bật của Thái Nguyên là hồ Núi Cốc, một hồ nước nhân tạo rộng lớn với cảnh quan thơ mộng, rất thích hợp để thư giãn và chèo thuyền. Thái Nguyên cũng có nhiều di tích lịch sử như khu di tích ATK Định Hóa, nơi từng là căn cứ địa cách mạng trong kháng chiến chống Pháp. Tỉnh này còn nổi tiếng với các lễ hội truyền thống như lễ hội Lồng Tồng, lễ hội đền Đội Cấn, thu hút đông đảo du khách. Khí hậu Thái Nguyên mang đặc trưng của miền Bắc, với bốn mùa rõ rệt, rất phù hợp để khám phá văn hóa và thiên nhiên. Ẩm thực Thái Nguyên nổi bật với các món như chè Tân Cương, bánh chưng Bờ Đậu, và cơm lam."""
                ),
                Destinations(
                    name="Thanh Hóa",
                    mood="active",
                    place="city",
                    location="central",
                    description="""Thanh Hóa là một tỉnh nằm ở khu vực Bắc Trung Bộ của Việt Nam, nổi tiếng với bề dày lịch sử và những danh lam thắng cảnh tuyệt đẹp. Thanh Hóa là quê hương của nhiều triều đại phong kiến Việt Nam, với thành nhà Hồ - một di sản văn hóa thế giới được UNESCO công nhận, là minh chứng cho kiến trúc quân sự thời trung cổ. Tỉnh này có bãi biển Sầm Sơn, một trong những bãi biển nổi tiếng nhất miền Trung, với bãi cát dài, nước biển trong xanh, và không khí sôi động, rất thích hợp để tắm biển và nghỉ dưỡng. Thanh Hóa cũng có khu bảo tồn thiên nhiên Pù Luông, với những cánh đồng lúa bậc thang, rừng nguyên sinh, và bản làng của người Thái, rất thích hợp để khám phá thiên nhiên. Tỉnh này còn nổi tiếng với các lễ hội truyền thống như lễ hội Lam Kinh, lễ hội đền Bà Triệu. Khí hậu Thanh Hóa mang đặc trưng của miền Trung, với mùa khô và mùa mưa rõ rệt, rất phù hợp để khám phá thiên nhiên và văn hóa. Ẩm thực Thanh Hóa nổi bật với các món như nem chua, chả tôm, và bánh khoái."""
                ),
                Destinations(
                    name="Thừa Thiên Huế",
                    mood="chill",
                    place="quiet",
                    location="central",
                    description="""Thừa Thiên Huế là một tỉnh nằm ở khu vực miền Trung Việt Nam, nổi tiếng với bề dày lịch sử và những giá trị văn hóa truyền thống. Huế từng là kinh đô của Việt Nam dưới triều đại nhà Nguyễn, với Đại Nội Huế - một di sản văn hóa thế giới được UNESCO công nhận, là nơi lưu giữ nét kiến trúc cung đình cổ kính. Huế cũng có nhiều lăng tẩm của các vua Nguyễn như lăng Tự Đức, lăng Khải Định, với kiến trúc độc đáo và không gian thanh tịnh. Tỉnh này còn có bãi biển Lăng Cô, một trong những vịnh biển đẹp nhất thế giới, với bãi cát trắng mịn, nước biển trong xanh, rất thích hợp để thư giãn. Huế cũng nổi tiếng với các làn điệu dân ca Huế trên sông Hương, và các lễ hội truyền thống như Festival Huế. Khí hậu Huế mang đặc trưng của miền Trung, với mùa khô và mùa mưa rõ rệt, rất phù hợp để khám phá văn hóa và thiên nhiên. Ẩm thực Huế nổi bật với các món như bún bò Huế, bánh bèo, và cơm hến."""
                ),
                Destinations(
                    name="Tiền Giang",
                    mood="chill",
                    place="river",
                    location="south",
                    description="""Tiền Giang là một tỉnh nằm ở khu vực đồng bằng sông Cửu Long, phía Nam Việt Nam, nổi tiếng với hệ thống sông ngòi, kênh rạch và những vườn cây trái trù phú. Địa hình Tiền Giang chủ yếu là đồng bằng, với đất đai màu mỡ, rất thuận lợi cho nông nghiệp, đặc biệt là trồng các loại cây ăn trái như sầu riêng, măng cụt, và chôm chôm. Một trong những điểm đến nổi bật của Tiền Giang là cù lao Thới Sơn, nơi du khách có thể trải nghiệm cuộc sống miền Tây với các hoạt động như chèo xuồng, nghe đờn ca tài tử, và thưởng thức trái cây tươi. Tiền Giang cũng có chợ nổi Cái Bè, một khu chợ trên sông tấp nập, thu hút du khách đến khám phá. Tỉnh này còn nổi tiếng với các di tích lịch sử như chùa Vĩnh Nghiêm, nhà Đốc Phủ Hải. Khí hậu Tiền Giang mang đặc trưng nhiệt đới gió mùa, với mùa khô và mùa mưa rõ rệt, rất phù hợp để khám phá thiên nhiên và văn hóa. Ẩm thực Tiền Giang nổi bật với các món như hủ tiếu Mỹ Tho, chả lụi, và bánh giá Chợ Giữa."""
                ),
                Destinations(
                    name="Trà Vinh",
                    mood="chill",
                    place="river",
                    location="south",
                    description="""Trà Vinh là một tỉnh nằm ở khu vực đồng bằng sông Cửu Long, phía Nam Việt Nam, nổi tiếng với những giá trị văn hóa đa dạng và cảnh sắc thiên nhiên yên bình. Địa hình Trà Vinh chủ yếu là đồng bằng, với đất đai màu mỡ, rất thuận lợi cho nông nghiệp, đặc biệt là trồng lúa và dừa. Một trong những điểm đến nổi bật của Trà Vinh là chùa Ông (chùa Chén Kiểu), một ngôi chùa của người Khmer với kiến trúc độc đáo, thu hút đông đảo du khách và phật tử. Trà Vinh cũng có ao Bà Om, một khu vực sinh thái với không gian yên bình, những cây sao cổ thụ, và không khí trong lành, rất thích hợp để thư giãn. Tỉnh này còn nổi tiếng với các lễ hội truyền thống như lễ hội Ok Om Bok, lễ hội cúng trăng rằm của người Khmer. Khí hậu Trà Vinh mang đặc trưng nhiệt đới gió mùa, với mùa khô và mùa mưa rõ rệt, rất phù hợp để khám phá văn hóa và thiên nhiên. Ẩm thực Trà Vinh nổi bật với các món như bún nước lèo, chù ụ, và bánh tét Trà Cuôn."""
                ),
                Destinations(
                    name="Tuyên Quang",
                    mood="chill",
                    place="mountain",
                    location="north",
                    description="""Tuyên Quang là một tỉnh nằm ở khu vực Đông Bắc Việt Nam, nổi tiếng với cảnh sắc thiên nhiên hùng vĩ và những giá trị văn hóa đa dạng. Địa hình Tuyên Quang chủ yếu là đồi núi, với những dãy núi cao và thung lũng xanh mướt, tạo nên một bức tranh thiên nhiên thơ mộng. Một trong những điểm đến nổi bật của Tuyên Quang là khu du lịch suối khoáng Mỹ Lâm, với những suối nước nóng tự nhiên, rất thích hợp để nghỉ dưỡng và thư giãn. Tuyên Quang cũng có nhiều di tích lịch sử như khu di tích Tân Trào, nơi từng là thủ đô kháng chiến trong Cách mạng Tháng Tám, thu hút đông đảo du khách. Tỉnh này còn nổi tiếng với các lễ hội truyền thống như lễ hội Lồng Tồng, lễ hội đua thuyền trên sông Lô. Khí hậu Tuyên Quang mang đặc trưng của miền Bắc, với mùa đông lạnh và mùa hè mát mẻ, rất phù hợp để khám phá thiên nhiên và văn hóa. Ẩm thực Tuyên Quang nổi bật với các món như cá bống sông Lô, bánh gai Chiêm Hóa, và thịt lợn đen."""
                ),
                Destinations(
                    name="Vĩnh Long",
                    mood="chill",
                    place="river",
                    location="south",
                    description="""Vĩnh Long là một tỉnh nằm ở khu vực đồng bằng sông Cửu Long, phía Nam Việt Nam, nổi tiếng với hệ thống sông ngòi, kênh rạch và những vườn cây trái trù phú. Địa hình Vĩnh Long chủ yếu là đồng bằng, với đất đai màu mỡ, rất thuận lợi cho nông nghiệp, đặc biệt là trồng các loại cây ăn trái như cam, quýt, và bưởi. Một trong những điểm đến nổi bật của Vĩnh Long là cù lao An Bình, nơi du khách có thể trải nghiệm cuộc sống miền Tây với các hoạt động như đi xuồng ba lá, tham quan vườn trái cây, và thưởng thức các món ăn dân dã. Vĩnh Long cũng có chùa Tiên Châu, một ngôi chùa cổ kính với kiến trúc độc đáo, thu hút đông đảo du khách và phật tử. Tỉnh này còn nổi tiếng với các làng nghề truyền thống như làm gốm đỏ, đan lát. Khí hậu Vĩnh Long mang đặc trưng nhiệt đới gió mùa, với mùa khô và mùa mưa rõ rệt, rất phù hợp để khám phá thiên nhiên và văn hóa. Ẩm thực Vĩnh Long nổi bật với các món như cá tai tượng chiên xù, lẩu mắm, và bưởi năm roi."""
                ),
                Destinations(
                    name="Vĩnh Phúc",
                    mood="chill",
                    place="mountain",
                    location="north",
                    description="""Vĩnh Phúc là một tỉnh nằm ở khu vực Đồng bằng sông Hồng, phía Bắc Việt Nam, nổi tiếng với những danh lam thắng cảnh và các giá trị văn hóa truyền thống. Địa hình Vĩnh Phúc đa dạng, với cả đồng bằng và đồi núi, tạo nên một bức tranh thiên nhiên phong phú. Một trong những điểm đến nổi bật của Vĩnh Phúc là Tam Đảo, một khu du lịch trên núi với khí hậu mát mẻ quanh năm, được mệnh danh là "Đà Lạt của miền Bắc", rất thích hợp để nghỉ dưỡng và khám phá thiên nhiên. Vĩnh Phúc cũng có nhiều di tích lịch sử và văn hóa như tháp Bình Sơn, chùa Hà Tiên, và khu danh thắng Tây Thiên, nơi kết hợp giữa cảnh quan thiên nhiên và tâm linh. Tỉnh này còn nổi tiếng với các làng nghề truyền thống như làm nón, dệt vải, và chạm khắc gỗ. Khí hậu Vĩnh Phúc mang đặc trưng của miền Bắc, với bốn mùa rõ rệt, rất phù hợp để khám phá văn hóa và thiên nhiên. Ẩm thực Vĩnh Phúc nổi bật với các món như cá thính Lập Thạch, bánh gio, và thịt bò tái kiến đốt."""
                ),
                Destinations(
                    name="Yên Bái",
                    mood="adventure",
                    place="mountain",
                    location="north",
                    description="""Yên Bái là một tỉnh nằm ở khu vực Tây Bắc Việt Nam, nổi tiếng với cảnh sắc thiên nhiên hùng vĩ và những giá trị văn hóa đa dạng. Địa hình Yên Bái chủ yếu là đồi núi, với những dãy núi cao và thung lũng xanh mướt, tạo nên một bức tranh thiên nhiên thơ mộng. Một trong những điểm đến nổi bật của Yên Bái là Mù Cang Chải, nơi có những ruộng bậc thang tuyệt đẹp, đặc biệt vào mùa lúa chín (tháng 9-10), được công nhận là danh thắng quốc gia. Yên Bái cũng có hồ Thác Bà, một trong những hồ nước nhân tạo lớn nhất Việt Nam, với cảnh quan thơ mộng và không khí yên bình, rất thích hợp để thư giãn. Tỉnh này còn nổi tiếng với các lễ hội truyền thống như lễ hội chọi trâu, lễ hội cầu mùa của người Thái. Khí hậu Yên Bái mang đặc trưng của miền Bắc, với mùa đông lạnh và mùa hè mát mẻ, rất phù hợp để khám phá thiên nhiên và văn hóa. Ẩm thực Yên Bái nổi bật với các món như xôi ngũ sắc, thịt trâu gác bếp, và măng sặt."""
                )

        ]

        db.session.bulk_save_objects(sample_destinations)
        db.session.commit()
        print("✅ Đã thêm dữ liệu mẫu vào bảng Destinations!") 




def search_from_db(mood, place, location):
    results = Destinations.query.filter_by(mood=mood, place=place, location=location).all()
    return [{"name": destination.name} for destination in results]

def extend_from_db(destination):
    results = Destinations.query.filter_by(name=destination).all()
    return [{"mood": dest.mood, "place": dest.place, "location": dest.location} for dest in results]

#Hàm bỏ dấu tiếng việt
def normalize(text):
    text = text.lower()
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn') # Loại bỏ dấu
    text = text.replace('đ', 'd') # thay đ bằng đ trong một số tỉnh như đồng nai, đà nẵng
    return text

#Hàm chuẩn hóa tên tỉnh, một số tỉnh bth dân việt nam hay viết tắt thì có thể tìm ra luôn
def standardize_province_name(name):
    normalized = normalize(name)

    aliases = {
        "hue": "Thừa Thiên Huế",
        "hcm": "Hồ Chí Minh",
        "hanoi": "Hà Nội",
        "hn": "Hà Nội",
        "sai gon": "Hồ Chí Minh"
    }

    return aliases.get(normalized, name)


def search_describe(province):
    try:

        standardized = standardize_province_name(province)
        normalized_input = normalize(standardized)
        all_destinations = Destinations.query.all()

        # Danh sách 5 TP trực thuộc TƯ
        city_list = ["Hà Nội", "Hồ Chí Minh", "Cần Thơ", "Hải Phòng", "Đà Nẵng"]
        city_normalized = [normalize(c) for c in city_list]

        for dest in all_destinations:
            if normalize(dest.name) == normalized_input:
                image_urls = [request.host_url.rstrip('/') + '/static/' + img.image_url for img in dest.images]
                
                # Nếu là 1 trong 5 TP thì thêm tiền tố "TP."
                display_name = f"TP. {dest.name}" if normalize(dest.name) in city_normalized else dest.name

                places = [
                    {
                        "name": dest.name,
                        "location": dest.location
                    }
                ]
                return [{
                    "name": display_name,
                    "describe": dest.description,
                    "images": image_urls,
                    "places": places

                }]
        return []

    except Exception as e:
        print(f"Error: {e}")
        return []