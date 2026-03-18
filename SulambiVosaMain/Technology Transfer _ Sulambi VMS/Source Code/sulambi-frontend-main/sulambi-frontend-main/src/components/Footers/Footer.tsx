import { useMediaQuery } from "react-responsive";

const Footer = () => {
  const isMobile = useMediaQuery({
    query: "(max-width: 600px)",
  });

  const iconStyle = {
    width: isMobile ? "15px" : "20px",
    height: isMobile ? "15px" : "20px",
    margin: "0px",
    borderRadius: "30%",
  };

  return (
    <footer>
      <div
        style={{
          width: "98%",
          margin: "auto",
          display: "flex",
          justifyContent: "space-between",
        }}
      >
        <span>Sulambi - VOSA © 2024</span>
        <div
          style={{
            display: "flex",
            gap: isMobile ? "15px" : "30px",
          }}
        >
          <a
            href="https://www.facebook.com/SulambiVOSA"
            target="_blank"
            rel="noopener noreferrer"
          >
            <img
              src="https://cdn-icons-png.flaticon.com/512/124/124010.png"
              alt="Facebook"
              style={iconStyle}
            />
          </a>
          <a href="mailto:sulambi-vosa@gmail.com">
            <img
              src="https://cdn-icons-png.flaticon.com/512/281/281769.png"
              alt="Gmail"
              style={iconStyle}
            />
          </a>
          <a href="https://www.x.com" target="_blank" rel="noopener noreferrer">
            <img
              src="https://cdn-icons-png.flaticon.com/512/733/733579.png"
              alt="Twitter"
              style={iconStyle}
            />
          </a>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
