import { Fragment, useState } from "react";
import { Button, Box } from "@mui/material";
import axios from 'axios';
import { API_GATEWAY } from '../config';

const PromptSubmit = () => {
  const [prompt, setField1] = useState('');
  const [filter, setField2] = useState('');
  const [data, setData] = useState(null);


  const handleSubmit = async () => {
    try {
      setData()
      const params = {
        prompt: prompt || "undefined",
        filter: filter || "undefined",
      };
      const response = await axios.get(`${API_GATEWAY}/kb`, {params},
      );
      console.log(response.data.body);
      setData(response.data);
      
      } catch (error) {
        console.error(error);
      }
  };

  return (
    <Box>
        <Fragment>
          <label>
            <label htmlFor="textField">Prompt:</label><br></br>
            <textarea
              type="text"
              value={prompt}
              onChange={(e) => setField1(e.target.value)}
              rows="5" 
              cols="33"
            /><br></br>
            <label htmlFor="textField">Disciplina: </label>
            <input
              type="text"
              value={filter}
              onChange={(e) => setField2(e.target.value)}
              placeholder="Insira a disciplina"
            /><br></br>
            <Button
              variant="contained"
              component="span"
              onClick={handleSubmit}
            >
              Enviar
            </Button>
            {data && (
              <div>
                <h2>Resposta:</h2>
                {data.body.answer.split('\n').map((paragraph, index) => (
                  <p key={index}>{paragraph}</p>
                ))}
                <hr></hr>
                <h3>Referências:</h3>

                {data.body.citations.map((citation, index) => (
                    <div key={index}>
                     {citation.retrievedReferences[0] &&
                        citation.retrievedReferences[0].location ? (
                          JSON.stringify(
                            citation.retrievedReferences[0].location.s3Location,null,2
                          )
                        ) : (
                          <span></span>
                        )}
                    </div>
                ))}
              </div>
            )}
          </label>
        </Fragment>
    </Box>
  );
};

export default PromptSubmit;
