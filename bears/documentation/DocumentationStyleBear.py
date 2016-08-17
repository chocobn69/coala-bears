from coalib.bearlib.languages.documentation.DocumentationComment import (
    DocumentationComment)
from coalib.bearlib.languages.documentation.DocstyleDefinition import (
    DocstyleDefinition)
from coalib.bearlib.languages.documentation.DocumentationExtraction import (
    extract_documentation)
from coalib.bears.LocalBear import LocalBear
from coalib.results.Diff import Diff
from coalib.results.Result import Result


class DocumentationStyleBear(LocalBear):
    LANGUAGES = {language for docstyle, language in
                 DocstyleDefinition.get_available_definitions()}
    AUTHORS = {'The coala developers'}
    AUTHORS_EMAILS = {'coala-devel@googlegroups.com'}
    LICENSE = 'AGPL-3.0'
    ASCIINEMA_URL = 'https://asciinema.org/a/7sfk3i9oxs1ixg2ncsu3pym0u'
    CAN_DETECT = {'Documentation'}

    def run(self, filename, file, docstyle: str, language: str):
        """
        Checks for certain in-code documentation styles.

        It currently checks for the following style: ::

            hello
            :param x:
                4 space indent
            :return:
                also 4 space indent
                following lines are also 4 space indented

        :param docstyle: The docstyle to use.
        :param language: The programming language of the file(s).
        """
        for doc_comment in extract_documentation(file, language, docstyle):
            metadata = iter(doc_comment.parse())

            # Assuming that the first element is always the only main
            # description.
            new_metadata = [next(metadata)]
            for m in metadata:
                # Split newlines and remove leading and trailing whitespaces.
                stripped_desc = list(map(str.strip, m.desc.splitlines()))

                if len(stripped_desc) == 0:
                    # Annotations should be on their own line, though no
                    # further description follows.
                    stripped_desc.append('')
                else:
                    # Wrap parameter description onto next line if it follows
                    # annotation directly.
                    if stripped_desc[0] != '':
                        stripped_desc.insert(0, '')

                # Indent with 4 spaces.
                stripped_desc = ('' if line == '' else ' ' * 4 + line for line
                                 in stripped_desc)

                new_desc = '\n'.join(stripped_desc)

                # Strip away trailing whitespaces and obsolete newlines (except
                # 1 newline which is mandatory).
                new_desc = new_desc.rstrip() + '\n'

                new_metadata.append(m._replace(desc=new_desc.lstrip(' ')))

            new_comment = DocumentationComment.from_metadata(
                new_metadata, doc_comment.docstyle_definition,
                doc_comment.marker, doc_comment.indent, doc_comment.range)

            if new_comment != doc_comment:
                # Something changed, let's apply a result.
                diff = Diff(file)

                # Delete the old comment
                diff.delete_lines(doc_comment.range.start.line,
                                  doc_comment.range.end.line)

                # Apply the new comment
                assembled = new_comment.assemble().splitlines(True)

                end_line = new_comment.range.end.line
                end_marker_pos = new_comment.range.end.column - 1
                diff.add_lines(new_comment.range.start.line, assembled[:-1])
                diff.add_lines(
                    end_line,
                    [assembled[-1] + file[end_line - 1][end_marker_pos:]])

                yield Result(
                    origin=self,
                    message="Documentation does not have correct style.",
                    affected_code=(diff.range(filename),),
                    diffs={filename: diff})
