import { Typography, Box, Container } from "@mui/material";
import ImageUploader from "../components/kbsubmit";

function Exams() {
  return (
    <Container
      disableGutters
      maxWidth="md"
      component="main"
      sx={{ pt: 8, pb: 6, pr: 4, pl: 4 }}
    >
      <Box display="flex" justifyContent="left">
        <Typography variant="h4">KnowledgeBase</Typography>
      </Box>
      <Box mt={2}>
        <ImageUploader />
      </Box>

    </Container>
  );
}

export default Exams;
