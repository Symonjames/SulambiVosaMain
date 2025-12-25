import { createContext, ReactNode, useState } from "react";
import { produce } from "immer";

interface Triplets {
  formData: any;
  setFormData: (value: any) => void;
  immutableSetFormData: (immutableVal: any) => void;
  mutableSetFormData: (mutableVal: any) => void;
  resetFormData: () => void;
}

export const FormDataContext = createContext<Triplets>({
  formData: {},
  setFormData: () => {},
  immutableSetFormData: () => {},
  mutableSetFormData: () => {},
  resetFormData: () => {},
});

const FormDataProvider = ({ children }: { children: ReactNode }) => {
  const [formData, setFormData] = useState({});

  const immutableSetFormData = (immutableVal: any) => {
    setFormData((prevData) =>
      produce(prevData, (draft) => {
        Object.assign(draft, immutableVal);
      })
    );
  };

  const mutableSetFormData = (immutableVal: any) => {
    setFormData((prevData) => ({ ...prevData, ...immutableVal }));
  };

  const resetFormData = () => {
    setFormData({});
  };

  return (
    <FormDataContext.Provider
      value={{
        formData,
        setFormData,
        immutableSetFormData,
        mutableSetFormData,
        resetFormData,
      }}
    >
      {children}
    </FormDataContext.Provider>
  );
};

export default FormDataProvider;
