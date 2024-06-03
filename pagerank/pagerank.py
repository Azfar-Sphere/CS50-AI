import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    # print(f"Corpus: {corpus}, Page: {page}")
    pd = dict.fromkeys(corpus, 0)
    links = [link for link in corpus[page]]

    if not links or len(links) == 0:
        eqpb = 1 / len(corpus)
        pd = {key: eqpb for key in pd}
        return pd

    dfp = damping_factor / len(links)
    one_m_dfp = (1 - damping_factor) / len(corpus)  

    dfp += one_m_dfp

    for key in pd:
        if key in links:
            pd[key] = dfp
        elif key not in links:
            pd[key] = one_m_dfp

    return pd 


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    samples = []
    pr = dict.fromkeys(corpus, 0)
    page = random.choice(list(corpus))
    samples.append(page)

    for i in range(n):
        tm = transition_model(corpus, page, damping_factor)

        probabilities = list(tm.values())
        pages = list(tm.keys())

        next_page = random.choices(pages, weights=probabilities, k=1)[0]
        samples.append(next_page)

        page = next_page

    for key in corpus:
        PageRank = samples.count(key) / n
        pr[key] = PageRank

    return pr


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    np = len(corpus)
    PR = dict.fromkeys(corpus, 1 / np)
    total_change = dict.fromkeys(corpus, False)

    while True:

        for page in PR:

            one_m_dp = (1 - damping_factor) / np

            if not corpus[page]:
                pages = corpus.keys()
                corpus[page] = pages

            list_i = [key for key, value in corpus.items() if page in value]
            sigma_pd = 0

            for i in list_i:
                NumLinks = len(corpus[i])
                pd = PR[i] / NumLinks

                sigma_pd += pd
            
            dpd = damping_factor * sigma_pd

            new_PR = one_m_dp + dpd
            change = abs(PR[page] - new_PR)
            if change < 0.001:
                total_change[page] = True

            PR[page] = new_PR
        
        if not any(value == False for value in total_change.values()):
            return PR

    
if __name__ == "__main__":
    main()
