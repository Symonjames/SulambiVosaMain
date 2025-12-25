import { Box } from "@mui/material";
import React, { useState } from "react";
import CustomButton from "../Buttons/CustomButton";
import ArrowCircleLeftIcon from "@mui/icons-material/ArrowCircleLeft";
import ArrowCircleRightIcon from "@mui/icons-material/ArrowCircleRight";
import { useMediaQuery } from "react-responsive";

const HorizontalCarousel = ({ children }: { children: React.ReactNode }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const totalCards = React.Children.count(children);
  const totalSlides = Math.ceil(totalCards / 3);

  const isMobile = useMediaQuery({
    query: "(max-width: 600px)",
  });

  const nextSlide = () => {
    if (currentIndex < totalSlides - 1) {
      setCurrentIndex((prevIndex) => prevIndex + 1);
    }
  };

  const prevSlide = () => {
    if (currentIndex > 0) {
      setCurrentIndex((prevIndex) => prevIndex - 1);
    }
  };

  return (
    <Box
      sx={{
        position: "relative",
        justifyContent: "space-around",
        overflow: "hidden",
        width: isMobile ? "98vw" : "85vw",
        padding: "10px 10px",
        margin: "auto",
      }}
    >
      <Box
        sx={{
          display: "flex",
          gap: "2.3em",
          transition: "transform 0.5s ease-in-out",
          transform: `translateX(-${currentIndex * 100}%)`,
          padding: "30px",
          overflow: isMobile ? "auto" : "",
        }}
      >
        {React.Children.map(children, (child) => (
          <Box sx={{ padding: 1 }}>{child}</Box>
        ))}
      </Box>
      {!isMobile && (
        <>
          <CustomButton
            onClick={prevSlide}
            startIcon={<ArrowCircleLeftIcon />}
            label="Prev"
            disabled={currentIndex === 0}
            sx={{
              zIndex: 1,
              left: 16,
              position: "absolute",
              color: "white",
              top: "50%",
              transform: "translateY(-50%)",
              backgroundColor:
                currentIndex === 0
                  ? "rgba(0, 0, 0, 0.2)"
                  : "rgba(0, 0, 0, 0.4)",
              borderRadius: "30px",
              "&:hover": {
                backgroundColor:
                  currentIndex === 0
                    ? "rgba(0, 0, 0, 0.2)"
                    : "rgba(0, 0, 0, 0.8)",
              },
            }}
          />
          <CustomButton
            onClick={nextSlide}
            endIcon={<ArrowCircleRightIcon />}
            label="Next"
            disabled={currentIndex === totalSlides - 1} // Disable button if at end
            sx={{
              zIndex: 1,
              right: 16,
              position: "absolute",
              color: "white",
              top: "50%",
              transform: "translateY(-50%)",
              backgroundColor:
                currentIndex === totalSlides - 1
                  ? "rgba(0, 0, 0, 0.2)"
                  : "rgba(0, 0, 0, 0.4)",
              borderRadius: "30px",
              "&:hover": {
                backgroundColor:
                  currentIndex === totalSlides - 1
                    ? "rgba(0, 0, 0, 0.2)"
                    : "rgba(0, 0, 0, 0.8)",
              },
            }}
          />
        </>
      )}
    </Box>
  );
};

export default HorizontalCarousel;
