import ReactSimpleImageViewer from "react-simple-image-viewer";

interface Props {
  open: boolean;
  imageSource: string;
  setOpen?: (state: boolean) => void;
  height?: string;
  width?: string;
}

const LocalImageViewer: React.FC<Props> = ({ open, imageSource, setOpen }) => {
  return (
    <>
      {open && (
        <ReactSimpleImageViewer
          closeOnClickOutside
          backgroundStyle={{
            zIndex: 10000, // Higher z-index to appear above other content
            backgroundColor: "rgba(0, 0, 0, 0.9)",
          }}
          onClose={() => setOpen && setOpen(false)}
          src={[imageSource]}
        />
      )}
    </>
  );
};

export default LocalImageViewer;
