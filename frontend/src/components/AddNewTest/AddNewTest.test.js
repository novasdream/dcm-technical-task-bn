import React from 'react';
import { fireEvent, render, waitFor } from '@testing-library/react';
import AddNewTest from './AddNewTest';
let file;

beforeEach(() => {
  file = new File(["(□_□)"], "testing.py", {type: "text/plain"});
});

test('Choose File exist on file', () => {
  const { getByTestId } = render(<AddNewTest />);
  const clickChooseFile = getByTestId(/newTestFile/i);
  expect(clickChooseFile).toBeInTheDocument();
});

test('Choose File exist on file', async () => {
  const ref = React.createRef()
  const { getByTestId } = render(<AddNewTest
    fileInput={ref}
    uploadTestFile={() => {}}
  />);
  
  const clickChooseFile = getByTestId(/newTestFile/i);
  fireEvent.change(clickChooseFile, {
    target: { files: [file] },
  })
  expect(ref.current.files[0]).toBe(file);
  expect(clickChooseFile).toBeInTheDocument();
});

test('Choose File exist on file', async () => {
  const uploadMockFunction = jest.fn();
  const ref = React.createRef()
  const { getByTestId } = render(<AddNewTest
    fileInput={ref}
    uploadTestFile={uploadMockFunction}
  />);
  
  const clickChooseFile = getByTestId(/newTestFile/i);
  fireEvent.change(clickChooseFile, {
    target: { files: [file] },
  })
  const submit = getByTestId(/submitButton/i);
  fireEvent.click(submit)
  expect(uploadMockFunction).toHaveBeenCalled();
  expect(clickChooseFile).toBeInTheDocument();
});
